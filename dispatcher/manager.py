"""Central Agent Manager: Process lifecycle, monitoring, logs, and registry."""

import os
import sys
import time
import signal
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Generator

from .config import (
    load_agents_config,
    save_agents_config,
    load_settings,
    PIDS_DIR,
    LOGS_DIR,
    HOME,
    EXCLUDED_AGENT_IDS
)
from .models import Agent, AgentLiveStatus
from .system_info import (
    is_port_in_use,
    get_pid_listening_on_port,
    get_network_urls,
    format_uptime,
    HAS_PSUTIL
)
from .detector import discover_all

if HAS_PSUTIL:
    import psutil


class AgentManager:
    def __init__(self):
        self.settings = load_settings()
        self._raw_agents = load_agents_config()
        self.agents: Dict[str, Agent] = {
            item["id"]: Agent.from_dict(item) for item in self._raw_agents
        }

    def reload(self):
        """Reload configuration from disk."""
        self.settings = load_settings()
        self._raw_agents = load_agents_config()
        self.agents = {
            item["id"]: Agent.from_dict(item) for item in self._raw_agents
        }

    def _check_and_heal_relocated_agent(self, agent: Agent) -> bool:
        """If a project folder was moved, find it in the configured scan directories and update its paths."""
        if not agent.working_dir:
            return False
        old_path = Path(agent.working_dir)
        if old_path.exists():
            return False

        folder_name = old_path.name
        scan_dirs = self.settings.get("scan_dirs", [
            str(HOME / "Projects"),
            str(HOME / "Downloads")
        ])

        candidates = []
        for s_dir in scan_dirs:
            base = Path(s_dir)
            if not base.exists():
                continue
            for cand in [base / folder_name, base / folder_name.lower(), base / folder_name.upper()]:
                if cand.exists() and cand.is_dir() and cand != old_path:
                    candidates.append(cand)

        for cand in candidates:
            has_app = (cand / "app" / "server.py").exists() or (cand / "app.py").exists() or any(cand.glob("*.sh"))
            if has_app:
                new_dir_str = str(cand.resolve())
                old_dir_str = str(old_path)
                agent.working_dir = new_dir_str
                if agent.start_cmd and old_dir_str in agent.start_cmd:
                    agent.start_cmd = agent.start_cmd.replace(old_dir_str, new_dir_str)
                # Persist updated paths
                for raw in self._raw_agents:
                    if raw.get("id") == agent.id:
                        raw["working_dir"] = agent.working_dir
                        raw["start_cmd"] = agent.start_cmd
                save_agents_config(self._raw_agents)
                return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        agent = self.agents.get(agent_id)
        if agent:
            self._check_and_heal_relocated_agent(agent)
        return agent

    def list_agents(self) -> List[Agent]:
        for agent in self.agents.values():
            self._check_and_heal_relocated_agent(agent)
        return list(self.agents.values())

    def get_pid_file(self, agent: Agent) -> Path:
        if agent.pid_file:
            return Path(agent.pid_file)
        return PIDS_DIR / f"{agent.id}.pid"

    def get_log_file(self, agent: Agent) -> Path:
        if agent.log_file:
            return Path(agent.log_file)
        return LOGS_DIR / f"{agent.id}.log"

    def _get_daemon_pid(self, agent: Agent) -> Optional[int]:
        """Check PID from PID file or active listening port."""
        pid_path = self.get_pid_file(agent)
        if pid_path.exists():
            try:
                pid = int(pid_path.read_text().strip())
                if HAS_PSUTIL and psutil.pid_exists(pid):
                    try:
                        # Verify process is still valid and not a zombie
                        proc = psutil.Process(pid)
                        if proc.status() != psutil.STATUS_ZOMBIE:
                            return pid
                    except Exception:
                        pass
                elif not HAS_PSUTIL:
                    try:
                        os.kill(pid, 0)
                        return pid
                    except (OSError, ProcessLookupError):
                        pass
                # PID is dead, remove stale file
                pid_path.unlink(missing_ok=True)
            except Exception:
                pass

        # Fallback: check if port is listening
        if agent.port and is_port_in_use(agent.port):
            listening_pid = get_pid_listening_on_port(agent.port)
            if listening_pid:
                # Cache detected PID
                try:
                    pid_path.parent.mkdir(parents=True, exist_ok=True)
                    pid_path.write_text(str(listening_pid))
                except Exception:
                    pass
                return listening_pid

        return None

    def _compute_agent_status(self, agent: Agent) -> AgentLiveStatus:
        urls = get_network_urls(agent.port) if agent.port else []
        log_f = str(self.get_log_file(agent)) if agent.type in ("daemon", "systemd") else None

        # 1. SYSTEMD UNIT
        if agent.type == "systemd" and agent.systemd_unit:
            unit = agent.systemd_unit
            cmd_flag = ["--user"] if agent.systemd_user else []
            try:
                out = subprocess.check_output(
                    ["systemctl"] + cmd_flag + ["is-active", unit],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if out == "active":
                    pid = None
                    try:
                        p_out = subprocess.check_output(
                            ["systemctl"] + cmd_flag + ["show", "-p", "MainPID", "--value", unit],
                            stderr=subprocess.DEVNULL
                        ).decode().strip()
                        if p_out.isdigit() and int(p_out) > 0:
                            pid = int(p_out)
                    except Exception:
                        pass

                    cpu, mem, uptime = self._get_proc_metrics(pid) if pid else (None, None, None)
                    port_active = is_port_in_use(agent.port) if agent.port else False
                    return AgentLiveStatus(
                        id=agent.id,
                        name=agent.name,
                        category=agent.category,
                        type=agent.type,
                        status="RUNNING",
                        status_icon="🟢",
                        is_running=True,
                        pid=pid,
                        cpu_percent=cpu,
                        memory_mb=mem,
                        uptime=uptime,
                        port=agent.port,
                        port_listening=port_active,
                        urls=urls,
                        log_file=log_f,
                        description=agent.description,
                        working_dir=agent.working_dir
                    )
                elif out == "failed":
                    return AgentLiveStatus(
                        id=agent.id,
                        name=agent.name,
                        category=agent.category,
                        type=agent.type,
                        status="FAILED",
                        status_icon="🔴",
                        port=agent.port,
                        urls=urls,
                        log_file=log_f,
                        description=agent.description,
                        working_dir=agent.working_dir,
                        error_message="Systemd unit is in failed state"
                    )
                else:
                    return AgentLiveStatus(
                        id=agent.id,
                        name=agent.name,
                        category=agent.category,
                        type=agent.type,
                        status="STOPPED",
                        status_icon="⚪",
                        port=agent.port,
                        urls=urls,
                        log_file=log_f,
                        description=agent.description,
                        working_dir=agent.working_dir
                    )
            except Exception:
                # Systemd command failed or service inactive
                return AgentLiveStatus(
                    id=agent.id,
                    name=agent.name,
                    category=agent.category,
                    type=agent.type,
                    status="STOPPED",
                    status_icon="⚪",
                    port=agent.port,
                    urls=urls,
                    log_file=log_f,
                    description=agent.description,
                    working_dir=agent.working_dir
                )

        # 2. DOCKER CONTAINER
        if agent.type == "docker" and agent.container_name:
            cname = agent.container_name
            try:
                out = subprocess.check_output(
                    ["docker", "inspect", "-f", "{{.State.Status}}", cname],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if out == "running":
                    port_active = is_port_in_use(agent.port) if agent.port else False
                    return AgentLiveStatus(
                        id=agent.id,
                        name=agent.name,
                        category=agent.category,
                        type=agent.type,
                        status="RUNNING",
                        status_icon="🟢",
                        is_running=True,
                        port=agent.port,
                        port_listening=port_active,
                        urls=urls,
                        description=agent.description
                    )
                else:
                    return AgentLiveStatus(
                        id=agent.id,
                        name=agent.name,
                        category=agent.category,
                        type=agent.type,
                        status="STOPPED",
                        status_icon="⚪",
                        port=agent.port,
                        urls=urls,
                        description=agent.description
                    )
            except Exception:
                return AgentLiveStatus(
                    id=agent.id,
                    name=agent.name,
                    category=agent.category,
                    type=agent.type,
                    status="STOPPED",
                    status_icon="⚪",
                    port=agent.port,
                    description=agent.description,
                    error_message=f"Docker container '{cname}' not found"
                )

        # 3. CLI TOOL
        if agent.type == "cli":
            run_cmd = agent.run_cmd or agent.id
            cmd_name = run_cmd.split()[0]
            in_path = shutil.which(cmd_name) is not None or Path(cmd_name).exists()
            return AgentLiveStatus(
                id=agent.id,
                name=agent.name,
                category=agent.category,
                type=agent.type,
                status="READY" if in_path else "MISSING",
                status_icon="⚡" if in_path else "⚠️",
                description=agent.description,
                working_dir=agent.working_dir,
                error_message=None if in_path else f"Executable '{cmd_name}' not found in PATH"
            )

        # 4. DAEMON (Background service)
        pid = self._get_daemon_pid(agent)
        port_active = is_port_in_use(agent.port) if agent.port else False

        if pid:
            cpu, mem, uptime = self._get_proc_metrics(pid)
            return AgentLiveStatus(
                id=agent.id,
                name=agent.name,
                category=agent.category,
                type=agent.type,
                status="RUNNING",
                status_icon="🟢",
                is_running=True,
                pid=pid,
                cpu_percent=cpu,
                memory_mb=mem,
                uptime=uptime,
                port=agent.port,
                port_listening=port_active,
                urls=urls,
                log_file=log_f,
                description=agent.description,
                working_dir=agent.working_dir
            )
        elif port_active:
            # Port is listening but PID not determined
            return AgentLiveStatus(
                id=agent.id,
                name=agent.name,
                category=agent.category,
                type=agent.type,
                status="RUNNING",
                status_icon="🟢",
                is_running=True,
                port=agent.port,
                port_listening=True,
                urls=urls,
                log_file=log_f,
                description=agent.description,
                working_dir=agent.working_dir
            )
        else:
            return AgentLiveStatus(
                id=agent.id,
                name=agent.name,
                category=agent.category,
                type=agent.type,
                status="STOPPED",
                status_icon="⚪",
                port=agent.port,
                urls=urls,
                log_file=log_f,
                description=agent.description,
                working_dir=agent.working_dir
            )

    def _get_proc_metrics(self, pid: int) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        if not HAS_PSUTIL:
            return (None, None, None)
        try:
            p = psutil.Process(pid)
            cpu = round(p.cpu_percent(interval=None), 1)
            mem = round(p.memory_info().rss / (1024 * 1024), 1)
            uptime = format_uptime(time.time() - p.create_time())
            return (cpu, mem, uptime)
        except Exception:
            return (None, None, None)

    def get_status(self, agent_id: str, lang: Optional[str] = None) -> AgentLiveStatus:
        """Fetch live status of an agent with optional i18n localization."""
        agent = self.get_agent(agent_id)
        if not agent:
            return AgentLiveStatus(
                id=agent_id,
                name=agent_id,
                category="unknown",
                type="unknown",
                status="MISSING",
                status_icon="❓",
                error_message=f"Agent '{agent_id}' not found in registry"
            )

        st = self._compute_agent_status(agent)
        from .i18n import get_agent_name, get_agent_description
        st.name = get_agent_name(agent, lang=lang)
        st.description = get_agent_description(agent, lang=lang)
        st.name_i18n = getattr(agent, "name_i18n", None)
        st.description_i18n = getattr(agent, "description_i18n", None)
        return st

    def list_all_status(self, lang: Optional[str] = None) -> List[AgentLiveStatus]:
        """Fetch live status for all registered agents."""
        return [self.get_status(aid, lang=lang) for aid in self.agents]

    def start(self, agent_id: str) -> Tuple[bool, str]:
        """Start an agent service."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False, f"Agent '{agent_id}' not found"

        st = self.get_status(agent_id)
        if st.is_running:
            return True, f"Agent '{agent.name}' is already running (PID: {st.pid or 'active'})"

        # Check for port conflicts before starting
        if agent.port and is_port_in_use(agent.port):
            return False, f"Port {agent.port} is already in use by another process!"

        # 1. Systemd unit
        if agent.type == "systemd" and agent.systemd_unit:
            cmd_flag = ["--user"] if agent.systemd_user else []
            try:
                subprocess.check_call(
                    ["systemctl"] + cmd_flag + ["start", agent.systemd_unit],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(1.2)
                st = self.get_status(agent_id)
                if st.is_running:
                    return True, f"Started '{agent.name}' via systemd unit {agent.systemd_unit}"
                else:
                    return False, f"Failed to start systemd unit {agent.systemd_unit}"
            except Exception as e:
                return False, f"Systemd error: {e}"

        # 2. Docker container
        if agent.type == "docker" and agent.container_name:
            try:
                subprocess.check_call(
                    ["docker", "start", agent.container_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(1.5)
                return True, f"Started Docker container '{agent.container_name}'"
            except Exception as e:
                return False, f"Docker error: {e}"

        # 3. CLI agents cannot be run as background daemons directly
        if agent.type == "cli":
            return False, f"Agent '{agent.name}' is a CLI tool. Use `agents run {agent.id}` instead."

        # 4. Custom start_cmd (e.g. repos start, suppliers start, or ./run.sh)
        work_dir = agent.working_dir or str(HOME)
        log_path = self.get_log_file(agent)
        pid_path = self.get_pid_file(agent)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        pid_path.parent.mkdir(parents=True, exist_ok=True)

        if agent.start_cmd:
            cmd = agent.start_cmd.strip()
            # If start_cmd handles its own daemonization (e.g. `repos start` or `./run.sh start`)
            if "start" in cmd.split():
                try:
                    res = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=work_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=15
                    )
                    time.sleep(1.5)
                    st = self.get_status(agent_id)
                    if st.is_running:
                        return True, f"Successfully started '{agent.name}' (PID: {st.pid})"
                except Exception as e:
                    return False, f"Error executing start command: {e}"

        # 5. Generic daemon launcher
        # Resolve python
        python_bin = "python3"
        if agent.venv_path:
            cand = Path(agent.venv_path) / "bin" / "python3"
            if not cand.exists():
                cand = Path(agent.venv_path) / "bin" / "python"
            if cand.exists():
                python_bin = str(cand)

        # Build command array
        cmd_str = agent.start_cmd or (f"{python_bin} app.py" if (Path(work_dir) / "app.py").exists() else None)
        if not cmd_str:
            return False, f"No start command or app.py found for '{agent.name}'"

        try:
            with open(log_path, "a", encoding="utf-8") as log_f:
                proc = subprocess.Popen(
                    cmd_str,
                    shell=True,
                    cwd=work_dir,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
            pid_path.write_text(str(proc.pid))
            time.sleep(1.2)

            # Check if alive
            if HAS_PSUTIL and psutil.pid_exists(proc.pid):
                return True, f"Successfully launched '{agent.name}' (PID: {proc.pid})"
            elif not HAS_PSUTIL:
                try:
                    os.kill(proc.pid, 0)
                    return True, f"Successfully launched '{agent.name}' (PID: {proc.pid})"
                except OSError:
                    pass

            # If died, read log error
            err_tail = self._read_log_tail(log_path, lines=4)
            return False, f"Process died immediately. Last log: {err_tail}"
        except Exception as e:
            return False, f"Failed to spawn process: {e}"

    def stop(self, agent_id: str) -> Tuple[bool, str]:
        """Stop an agent service."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False, f"Agent '{agent_id}' not found"

        st = self.get_status(agent_id)
        if not st.is_running:
            return True, f"Agent '{agent.name}' is already stopped"

        # 1. Systemd unit
        if agent.type == "systemd" and agent.systemd_unit:
            cmd_flag = ["--user"] if agent.systemd_user else []
            try:
                subprocess.check_call(
                    ["systemctl"] + cmd_flag + ["stop", agent.systemd_unit],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.8)
                return True, f"Stopped systemd unit '{agent.systemd_unit}'"
            except Exception as e:
                return False, f"Failed to stop systemd unit: {e}"

        # 2. Docker container
        if agent.type == "docker" and agent.container_name:
            try:
                subprocess.check_call(
                    ["docker", "stop", agent.container_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, f"Stopped Docker container '{agent.container_name}'"
            except Exception as e:
                return False, f"Failed to stop Docker container: {e}"

        # 3. Custom stop_cmd
        if agent.stop_cmd:
            try:
                subprocess.run(
                    agent.stop_cmd,
                    shell=True,
                    cwd=agent.working_dir or str(HOME),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10
                )
                time.sleep(1)
                st = self.get_status(agent_id)
                if not st.is_running:
                    self.get_pid_file(agent).unlink(missing_ok=True)
                    return True, f"Stopped '{agent.name}' via stop command"
            except Exception:
                pass

        # 4. Process termination via PID
        pid = st.pid or self._get_daemon_pid(agent)
        if pid:
            try:
                # Terminate entire process group
                try:
                    pgid = os.getpgid(pid)
                    os.killpg(pgid, signal.SIGTERM)
                except Exception:
                    os.kill(pid, signal.SIGTERM)

                # Wait up to 4 seconds
                for _ in range(20):
                    time.sleep(0.2)
                    if HAS_PSUTIL and not psutil.pid_exists(pid):
                        break
                    elif not HAS_PSUTIL:
                        try:
                            os.kill(pid, 0)
                        except OSError:
                            break
                else:
                    # Still alive, send SIGKILL
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                    except Exception:
                        os.kill(pid, signal.SIGKILL)

                self.get_pid_file(agent).unlink(missing_ok=True)
                return True, f"Stopped '{agent.name}' (PID: {pid})"
            except Exception as e:
                return False, f"Failed to terminate PID {pid}: {e}"

        return False, f"Could not determine PID to stop '{agent.name}'"

    def restart(self, agent_id: str) -> Tuple[bool, str]:
        """Restart an agent service."""
        stop_ok, stop_msg = self.stop(agent_id)
        time.sleep(1.2)
        start_ok, start_msg = self.start(agent_id)
        if start_ok:
            return True, f"Restarted successfully. {start_msg}"
        return False, f"Restart failed: {start_msg}"

    def get_logs(self, agent_id: str, lines: int = 50) -> List[str]:
        """Fetch the last N log lines for an agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return [f"Agent '{agent_id}' not found."]

        # 1. Systemd logs
        if agent.type == "systemd" and agent.systemd_unit:
            cmd_flag = ["--user"] if agent.systemd_user else []
            try:
                out = subprocess.check_output(
                    ["journalctl"] + cmd_flag + ["-u", agent.systemd_unit, "-n", str(lines), "--no-pager"],
                    stderr=subprocess.STDOUT
                ).decode("utf-8", errors="replace")
                return out.splitlines()
            except Exception as e:
                return [f"Error fetching systemd journal: {e}"]

        # 2. Docker logs
        if agent.type == "docker" and agent.container_name:
            try:
                out = subprocess.check_output(
                    ["docker", "logs", "--tail", str(lines), agent.container_name],
                    stderr=subprocess.STDOUT
                ).decode("utf-8", errors="replace")
                return out.splitlines()
            except Exception as e:
                return [f"Error fetching docker logs: {e}"]

        # 3. Log file
        log_path = self.get_log_file(agent)
        if not log_path.exists():
            return [f"No log file found at {log_path} yet."]

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
                return [line.rstrip("\r\n") for line in all_lines[-lines:]]
        except Exception as e:
            return [f"Error reading log file: {e}"]

    def _read_log_tail(self, log_path: Path, lines: int = 3) -> str:
        if not log_path.exists():
            return ""
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                tail = f.readlines()[-lines:]
                return " ".join(line.strip() for line in tail)
        except Exception:
            return ""

    def open_browser(self, agent_id: str) -> Tuple[bool, str]:
        """Open web application in browser."""
        agent = self.get_agent(agent_id)
        if not agent:
            return False, f"Agent '{agent_id}' not found"

        url = agent.url or (f"http://localhost:{agent.port}" if agent.port else None)
        if not url:
            return False, f"No URL or port configured for '{agent.name}'"

        try:
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Opened {url} in browser"
        except Exception:
            try:
                webbrowser.open(url)
                return True, f"Opened {url} in browser"
            except Exception as e:
                return False, f"Failed to open browser: {e}"

    def run_cli(self, agent_id: str, extra_args: List[str]) -> int:
        """Run CLI agent interactively in foreground."""
        agent = self.get_agent(agent_id)
        if not agent:
            print(f"Error: Agent '{agent_id}' not found.", file=sys.stderr)
            return 1

        cmd_base = agent.run_cmd or agent.start_cmd or agent.id
        full_cmd = f"{cmd_base} {' '.join(extra_args)}".strip()
        work_dir = agent.working_dir or str(HOME)

        print(f"⚡ Launching {agent.name}: {full_cmd}\n")
        try:
            return subprocess.call(full_cmd, shell=True, cwd=work_dir)
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            print(f"Execution error: {e}", file=sys.stderr)
            return 1

    def scan_for_microapps(self) -> List[Dict[str, Any]]:
        """Run discovery scan across configured directories."""
        dirs = self.settings.get("scan_dirs", [])
        return discover_all(dirs, list(self.agents.values()))

    def add_agent(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Register a new agent."""
        agent_id = data.get("id", "").strip().lower()
        if not agent_id:
            return False, "Agent ID cannot be empty"

        if agent_id in EXCLUDED_AGENT_IDS:
            return False, f"'{agent_id}' is an AI coding CLI and is excluded from the dispatcher"

        if agent_id in self.agents:
            return False, f"Agent '{agent_id}' is already registered"

        agent = Agent.from_dict(data)
        self.agents[agent_id] = agent
        self._raw_agents.append(agent.to_dict())
        save_agents_config(self._raw_agents)
        return True, f"Agent '{agent.name}' ({agent_id}) successfully registered"

    def remove_agent(self, agent_id: str) -> Tuple[bool, str]:
        """Unregister an agent, stopping it if running."""
        if agent_id not in self.agents:
            return False, f"Agent '{agent_id}' not found"

        # Stop if running
        self.stop(agent_id)

        name = self.agents[agent_id].name
        del self.agents[agent_id]
        self._raw_agents = [a for a in self._raw_agents if a.get("id") != agent_id]
        save_agents_config(self._raw_agents)
        return True, f"Agent '{name}' ({agent_id}) removed from registry"
