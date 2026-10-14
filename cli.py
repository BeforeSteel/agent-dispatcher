#!/usr/bin/env python3
"""
Agent Dispatcher CLI - manage agents and micro-apps from the command line
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Ensure dispatcher package can be imported
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dispatcher.manager import AgentManager
from dispatcher.system_info import get_system_stats, get_network_ips
from dispatcher.i18n import t, get_current_lang, SUPPORTED_LANGUAGES

# Terminal Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[1;32m"
C_BLUE = "\033[1;34m"
C_CYAN = "\033[1;36m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_PURPLE = "\033[1;35m"


def print_header(title: str):
    print(f"\n{C_BOLD}{C_CYAN}⬡ {title}{C_RESET}")
    print(f"{C_DIM}{'─' * 84}{C_RESET}")


def cmd_list(manager: AgentManager, args):
    """Display table of all agents and their live status."""
    lang = getattr(args, "lang", None) or get_current_lang()
    statuses = manager.list_all_status(lang=lang)
    if not statuses:
        print(f"\n{C_YELLOW}{t('cli.empty_registry', lang=lang)}{C_RESET}\n")
        return

    # Count stats
    running_count = sum(1 for s in statuses if s.is_running)
    ready_count = sum(1 for s in statuses if s.status == "READY")
    total_count = len(statuses)

    header_title = t("cli.header", lang=lang)
    w_active = t("cli.active_agents", lang=lang)
    w_cli = t("cli.cli_tools", lang=lang)
    w_total = t("cli.total", lang=lang)

    print(f"\n{C_BOLD}⬡ {header_title}{C_RESET} {C_DIM}({running_count} {w_active} · {ready_count} {w_cli} · {w_total} {total_count}){C_RESET}")
    print(f"{C_DIM}{'═' * 84}{C_RESET}")

    c_stat = t("cli.col.status", lang=lang)
    c_id = t("cli.col.id", lang=lang)
    c_name = t("cli.col.name", lang=lang)
    c_type = t("cli.col.type", lang=lang)
    c_port = t("cli.col.port", lang=lang)
    c_pid = t("cli.col.pid", lang=lang)
    c_res = t("cli.col.res", lang=lang)

    print(f"{C_BOLD}{C_BLUE}{c_stat:<5} {c_id:<16} {c_name:<22} {c_type:<10} {c_port:<8} {c_pid:<8} {c_res:<14}{C_RESET}")
    print(f"{C_DIM}{'─' * 84}{C_RESET}")

    for s in sorted(statuses, key=lambda x: (not x.is_running, x.status != "READY", x.id)):
        icon_str = "🟢" if s.status == "RUNNING" else ("⚡" if s.status == "READY" else ("🔴" if s.status == "FAILED" else "⚪"))
        id_fmt = f"{C_BOLD}{s.id:<16}{C_RESET}" if s.is_running else f"{s.id:<16}"
        name_fmt = f"{s.name[:21]:<22}"

        type_color = C_YELLOW if s.type == "systemd" else (C_PURPLE if s.type == "docker" else C_BLUE)
        type_fmt = f"{type_color}{s.type:<10}{C_RESET}"

        port_str = str(s.port) if s.port else "—"
        port_fmt = f"{port_str:<8}"

        pid_str = str(s.pid) if s.pid else "—"
        pid_fmt = f"{pid_str:<8}"

        if s.is_running:
            if s.memory_mb is not None:
                res_str = f"{s.memory_mb:.0f}MB/{s.cpu_percent:.0f}%"
            else:
                res_str = "active"
            res_fmt = f"{C_GREEN}{res_str:<14}{C_RESET}"
        elif s.status == "READY":
            res_fmt = f"{C_CYAN}{'CLI Tool':<14}{C_RESET}"
        else:
            res_fmt = f"{C_DIM}{'offline':<14}{C_RESET}"

        print(f" {icon_str}  {id_fmt} {name_fmt} {type_fmt} {port_fmt} {pid_fmt} {res_fmt}")

    print(f"{C_DIM}{'─' * 84}{C_RESET}")
    print(f"{C_DIM}{t('cli.commands_hint', lang=lang)}{C_RESET}\n")


def cmd_status(manager: AgentManager, args):
    """Detailed status inspection of an agent."""
    lang = getattr(args, "lang", None) or get_current_lang()
    if not args.agent_id:
        cmd_list(manager, args)
        return

    agent = manager.get_agent(args.agent_id)
    if not agent:
        print(f"{C_RED}❌ {t('cli.agent_not_found', id=args.agent_id)}{C_RESET}")
        return

    st = manager.get_status(args.agent_id, lang=lang)

    title_txt = t("cli.status_agent", lang=lang)
    print_header(f"{title_txt}: {st.name} ({agent.id})")
    print(f"  {C_BOLD}{t('cli.description', lang=lang)}:{C_RESET}        {st.description or '—'}")
    print(f"  {C_BOLD}{t('cli.category', lang=lang)}:{C_RESET}   {agent.category}  |  {C_BOLD}{t('cli.col.type', lang=lang)}:{C_RESET} {agent.type}")

    if st.status == "RUNNING":
        status_line = f"{C_GREEN}🟢 {t('cli.running_state', lang=lang)}{C_RESET}"
    elif st.status == "READY":
        status_line = f"{C_CYAN}⚡ {t('cli.ready_state', lang=lang)}{C_RESET}"
    elif st.status == "FAILED":
        status_line = f"{C_RED}🔴 {t('cli.failed_state', lang=lang)}{C_RESET}"
    else:
        status_line = f"{C_YELLOW}⚪ {t('cli.stopped_state', lang=lang)}{C_RESET}"
    print(f"  {C_BOLD}{t('cli.col.status', lang=lang)}:{C_RESET}      {status_line}")

    if st.pid:
        print(f"  {C_BOLD}{t('cli.col.pid', lang=lang)}:{C_RESET}         {st.pid}")
    if st.uptime:
        print(f"  {C_BOLD}{t('card.uptime', lang=lang)}:{C_RESET}      {st.uptime}")
    if st.memory_mb is not None:
        print(f"  {C_BOLD}{t('card.memory', lang=lang)}:{C_RESET}     {st.memory_mb:.1f} MB (RSS)")
    if st.cpu_percent is not None:
        print(f"  {C_BOLD}{t('card.cpu', lang=lang)}:{C_RESET}         {st.cpu_percent:.1f}%")

    if agent.port:
        port_state = f"{C_GREEN}Active{C_RESET}" if st.port_listening else f"{C_DIM}Inactive{C_RESET}"
        print(f"  {C_BOLD}{t('cli.port', lang=lang)}:{C_RESET}        {agent.port} ({port_state})")

    if st.urls:
        print(f"  {C_BOLD}{t('cli.urls', lang=lang)}:{C_RESET}")
        for u in st.urls:
            print(f"               • {u['label']:<16} {C_CYAN}{u['url']}{C_RESET}")

    if agent.working_dir:
        print(f"  {C_BOLD}{t('cli.dir', lang=lang)}:{C_RESET}     {agent.working_dir}")
    if agent.venv_path:
        print(f"  {C_BOLD}Virtualenv:{C_RESET}  {agent.venv_path}")

    log_path = manager.get_log_file(agent)
    if log_path.exists():
        print(f"  {C_BOLD}{t('cli.log_file', lang=lang)}:{C_RESET}  {log_path}")
        print(f"\n  {C_BOLD}{C_BLUE}{t('cli.recent_logs', lang=lang)}:{C_RESET}")
        print(f"  {C_DIM}{'┄' * 70}{C_RESET}")
        recent_logs = manager.get_logs(args.agent_id, lines=8)
        for line in recent_logs:
            print(f"    {C_DIM}{line}{C_RESET}")
        print(f"  {C_DIM}{'┄' * 70}{C_RESET}")

    print()


def cmd_start(manager: AgentManager, args):
    """Start an agent or all agents."""
    if args.agent_id.lower() == "all":
        print(f"\n{C_BOLD}🚀 {t('cli.start_all')}{C_RESET}")
        for agent in manager.list_agents():
            if agent.type in ("daemon", "systemd", "docker"):
                ok, msg = manager.start(agent.id)
                prefix = f"{C_GREEN}✅" if ok else f"{C_RED}❌"
                print(f"  {prefix} {agent.name:<22}: {msg}{C_RESET}")
        print()
        return

    ok, msg = manager.start(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}")
        st = manager.get_status(args.agent_id)
        if st.urls:
            for u in st.urls:
                print(f"   🌐 {u['label']}: {C_CYAN}{u['url']}{C_RESET}")
        print()
    else:
        print(f"\n{C_RED}❌ {t('cli.start_failed', msg=msg)}{C_RESET}\n")
        sys.exit(1)


def cmd_stop(manager: AgentManager, args):
    """Stop an agent or all agents."""
    if args.agent_id.lower() == "all":
        print(f"\n{C_BOLD}⏹ {t('cli.stop_all')}{C_RESET}")
        for agent in manager.list_agents():
            st = manager.get_status(agent.id)
            if st.is_running:
                ok, msg = manager.stop(agent.id)
                prefix = f"{C_GREEN}✅" if ok else f"{C_RED}❌"
                print(f"  {prefix} {agent.name:<22}: {msg}{C_RESET}")
        print()
        return

    ok, msg = manager.stop(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ {t('cli.stop_failed', msg=msg)}{C_RESET}\n")
        sys.exit(1)


def cmd_restart(manager: AgentManager, args):
    """Restart an agent."""
    print(f"\n{C_YELLOW}🔄 {t('cli.restarting', id=args.agent_id)}{C_RESET}")
    ok, msg = manager.restart(args.agent_id)
    if ok:
        print(f"{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"{C_RED}❌ {msg}{C_RESET}\n")
        sys.exit(1)


def cmd_logs(manager: AgentManager, args):
    """Display logs or follow stream."""
    agent = manager.get_agent(args.agent_id)
    if not agent:
        print(f"{C_RED}❌ {t('cli.agent_not_found', id=args.agent_id)}{C_RESET}")
        return

    lines = args.lines or 50
    if not args.follow:
        log_lines = manager.get_logs(args.agent_id, lines=lines)
        print_header(t("cli.logs_title", name=agent.name, n=len(log_lines)))
        for l in log_lines:
            print(l)
        print()
    else:
        print_header(t("cli.logs_follow_title", name=agent.name))
        # Show initial chunk
        initial = manager.get_logs(args.agent_id, lines=20)
        for l in initial:
            print(l)

        log_path = manager.get_log_file(agent)
        if not log_path.exists():
            print(f"{C_YELLOW}{t('cli.logs_waiting')}{C_RESET}")

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        print(line, end="")
                    else:
                        time.sleep(0.3)
        except KeyboardInterrupt:
            print(f"\n{C_DIM}{t('cli.logs_follow_done')}{C_RESET}\n")


def cmd_open(manager: AgentManager, args):
    """Open web interface in browser."""
    ok, msg = manager.open_browser(args.agent_id)
    if ok:
        print(f"{C_GREEN}🌐 {msg}{C_RESET}")
    else:
        print(f"{C_RED}❌ {msg}{C_RESET}")


def cmd_run(manager: AgentManager, args):
    """Run CLI tool or agent."""
    code = manager.run_cli(args.agent_id, args.extra_args)
    sys.exit(code)


def cmd_scan(manager: AgentManager, args):
    """Scan filesystem for micro-applications and agents."""
    print(f"\n{C_BOLD}🔍 {t('cli.scanning')}{C_RESET}")
    candidates = manager.scan_for_microapps()

    new_found = [c for c in candidates if not c.get("is_registered")]
    already_reg = [c for c in candidates if c.get("is_registered")]

    print(f"{C_DIM}{'─' * 84}{C_RESET}")
    if new_found:
        print(f"\n{C_BOLD}{C_GREEN}✨ {t('cli.scan_found', n=len(new_found))}{C_RESET}")
        print(f"{C_BOLD}{C_BLUE}{t('cli.col.id'):<16} {t('cli.col.name'):<24} {t('cli.col.type'):<10} {t('cli.col.port'):<8} {t('cli.col.dir')}{C_RESET}")
        print(f"{C_DIM}{'─' * 84}{C_RESET}")
        for c in new_found:
            port_s = str(c.get("port") or "—")
            print(f" {C_YELLOW}{c['id']:<16}{C_RESET} {c['name'][:23]:<24} {c['type']:<10} {port_s:<8} {C_DIM}{c.get('working_dir') or '—'}{C_RESET}")

        print(f"\n{C_BOLD}{t('cli.scan_add_hint')}{C_RESET}")
        print(f"  {C_CYAN}agents add --id {new_found[0]['id']}{C_RESET}")
    else:
        print(f"\n{C_GREEN}{t('cli.scan_all_registered')}{C_RESET}")

    if already_reg:
        print(f"\n{C_DIM}{t('cli.scan_already_count', n=len(already_reg))}{C_RESET}\n")


def cmd_add(manager: AgentManager, args):
    """Register a new agent."""
    # Check if candidate exists from scan
    if args.id:
        candidates = manager.scan_for_microapps()
        match = next((c for c in candidates if c["id"] == args.id), None)
        if match and match.get("is_registered"):
            print(f"{C_YELLOW}⚠️  {t('cli.already_registered_as', id=args.id, existing=match['registered_as'])}{C_RESET}")
            return
        if match:
            ok, msg = manager.add_agent(match)
            if ok:
                print(f"{C_GREEN}✅ {msg}{C_RESET}")
            else:
                print(f"{C_RED}❌ {msg}{C_RESET}")
            return

    # Interactive or flags
    agent_id = args.id or input(t("cli.prompt_id")).strip()
    if not agent_id:
        print(f"{C_RED}{t('cli.id_empty')}{C_RESET}")
        return

    name = args.name or input(t("cli.prompt_name")).strip() or agent_id
    work_dir = args.dir or input(t("cli.prompt_dir")).strip() or None
    port = int(args.port) if args.port else None
    app_type = args.type or ("web_app" if port else "daemon")

    data = {
        "id": agent_id,
        "name": name,
        "type": app_type,
        "working_dir": work_dir,
        "port": port,
        "url": f"http://localhost:{port}" if port else None,
        "start_cmd": args.start_cmd or None,
        "description": args.desc or t("cli.default_desc", name=name)
    }

    ok, msg = manager.add_agent(data)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ {msg}{C_RESET}\n")


def cmd_remove(manager: AgentManager, args):
    """Remove agent from registry."""
    ok, msg = manager.remove_agent(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ {msg}{C_RESET}\n")


def cmd_health(manager: AgentManager, args):
    """Check host system health and resources."""
    stats = get_system_stats()
    print_header(t("cli.health_title", host=stats.get("hostname")))
    print(f"  {C_BOLD}{t('cli.health_cpu')}:{C_RESET} {stats.get('cpu_percent')}% ({stats.get('cpu_count')} {t('stats.cores')})")
    if "memory_total_gb" in stats:
        print(f"  {C_BOLD}{t('cli.health_ram')}:{C_RESET} {stats.get('memory_used_gb')} GB / {stats.get('memory_total_gb')} GB ({stats.get('memory_percent')}%)")

    gpu = stats.get("gpu")
    if gpu:
        gpu_load = f"{t('cli.health_gpu_load')}:"
        vram = f"{t('cli.health_vram')}:"
        temp = f"{t('cli.health_temp')}:"
        width = max(len(gpu_load), len(vram), len(temp)) + 1
        print(f"\n  {C_BOLD}{t('cli.health_gpu', name=gpu.get('name'))}:{C_RESET}")
        print(f"    • {gpu_load:<{width}}{C_GREEN}{gpu.get('gpu_util_percent')}%{C_RESET}")
        print(f"    • {vram:<{width}}{C_CYAN}{gpu.get('mem_used_gb')} GB{C_RESET} / {gpu.get('mem_total_gb')} GB ({gpu.get('mem_percent')}%)")
        print(f"    • {temp:<{width}}{C_YELLOW}{gpu.get('temperature_c')}°C{C_RESET} ({t('cli.health_power')}: {gpu.get('power_w')}W / {gpu.get('power_limit_w')}W)")

    disks = stats.get("disks", {})
    if disks:
        print(f"\n  {C_BOLD}{t('cli.health_disks')}:{C_RESET}")
        for path, du in disks.items():
            usage = t("cli.health_disk_line", free=du["free_gb"], total=du["total_gb"], percent=du["percent"])
            print(f"    • {path:<20} {usage}")

    ips = stats.get("ips", {})
    print(f"\n  {C_BOLD}{t('cli.health_net')}:{C_RESET}")
    for k, v in ips.items():
        print(f"    • {k.upper():<12} {C_CYAN}{v}{C_RESET}")
    print()


def cmd_lang(manager: AgentManager, args):
    """View or set interface language."""
    from dispatcher.config import save_settings

    if not getattr(args, "code", None):
        cur = get_current_lang()
        print(f"\n🌍 {t('cli.lang_current')}: {C_BOLD}{C_CYAN}{cur.upper()}{C_RESET}")
        print(f"   {t('cli.lang_supported')}: {', '.join(SUPPORTED_LANGUAGES)}")
        print(f"   {t('cli.lang_switch')}: {C_YELLOW}agents lang <uk|en|ru>{C_RESET}\n")
        return

    code = args.code.lower()
    if code not in SUPPORTED_LANGUAGES:
        print(f"{C_RED}❌ {t('cli.lang_unsupported', code=code, available=', '.join(SUPPORTED_LANGUAGES))}{C_RESET}")
        return

    settings = manager.settings
    settings["lang"] = code
    save_settings(settings)
    print(f"{C_GREEN}✅ {t('cli.lang_changed', lang=code, code=code.upper())}{C_RESET}\n")


def cmd_web(manager: AgentManager, args):
    """Start the Web Dashboard interface."""
    from dispatcher.web_server import run_web_dashboard
    port = args.port or manager.settings.get("web_port", 8800)
    host = args.host or manager.settings.get("web_host", "127.0.0.1")
    run_web_dashboard(manager, host=host, port=port)


def argv_lang(argv) -> str:
    """Language passed with --lang, read before argparse so that its help is translated too."""
    for i, arg in enumerate(argv):
        if arg == "--lang" and i + 1 < len(argv):
            value = argv[i + 1]
        elif arg.startswith("--lang="):
            value = arg.split("=", 1)[1]
        else:
            continue
        if value in SUPPORTED_LANGUAGES:
            return value
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agents", description=t("cli.help.description"))
    parser.add_argument("--lang", choices=SUPPORTED_LANGUAGES, help=t("cli.help.lang"))
    sub = parser.add_subparsers(dest="command", help=t("cli.help.command"))

    # lang
    p_lang = sub.add_parser("lang", help=t("cli.help.lang_cmd"))
    p_lang.add_argument("code", nargs="?", choices=SUPPORTED_LANGUAGES, help=t("cli.help.lang_code"))

    # list
    p_list = sub.add_parser("list", aliases=["ls", "ps"], help=t("cli.help.list"))

    # status
    p_status = sub.add_parser("status", help=t("cli.help.status"))
    p_status.add_argument("agent_id", nargs="?", default=None, help=t("cli.help.agent_id"))

    # start
    p_start = sub.add_parser("start", help=t("cli.help.start"))
    p_start.add_argument("agent_id", help=t("cli.help.agent_id_or_all"))

    # stop
    p_stop = sub.add_parser("stop", help=t("cli.help.stop"))
    p_stop.add_argument("agent_id", help=t("cli.help.agent_id_or_all"))

    # restart
    p_restart = sub.add_parser("restart", help=t("cli.help.restart"))
    p_restart.add_argument("agent_id", help=t("cli.help.agent_id"))

    # logs
    p_logs = sub.add_parser("logs", help=t("cli.help.logs"))
    p_logs.add_argument("agent_id", help=t("cli.help.agent_id"))
    p_logs.add_argument("-n", "--lines", type=int, default=50, help=t("cli.help.lines"))
    p_logs.add_argument("-f", "--follow", action="store_true", help=t("cli.help.follow"))

    # open
    p_open = sub.add_parser("open", help=t("cli.help.open"))
    p_open.add_argument("agent_id", help=t("cli.help.agent_id"))

    # run
    p_run = sub.add_parser("run", help=t("cli.help.run"))
    p_run.add_argument("agent_id", help=t("cli.help.agent_id"))
    p_run.add_argument("extra_args", nargs="*", help=t("cli.help.extra_args"))

    # scan
    sub.add_parser("scan", aliases=["discover"], help=t("cli.help.scan"))

    # add
    p_add = sub.add_parser("add", help=t("cli.help.add"))
    p_add.add_argument("--id", help=t("cli.help.agent_id"))
    p_add.add_argument("--name", help=t("cli.help.name"))
    p_add.add_argument("--dir", help=t("cli.help.dir"))
    p_add.add_argument("--port", type=int, help=t("cli.help.port"))
    p_add.add_argument("--type", choices=["daemon", "systemd", "cli", "docker"], help=t("cli.help.type"))
    p_add.add_argument("--start-cmd", help=t("cli.help.start_cmd"))
    p_add.add_argument("--desc", help=t("cli.help.desc"))

    # remove
    p_rm = sub.add_parser("remove", aliases=["rm", "delete"], help=t("cli.help.remove"))
    p_rm.add_argument("agent_id", help=t("cli.help.agent_id"))

    # health
    sub.add_parser("health", help=t("cli.help.health"))

    # web: no argparse defaults, so web_host / web_port from settings.json apply
    p_web = sub.add_parser("web", aliases=["gui", "dashboard"], help=t("cli.help.web"))
    p_web.add_argument("-p", "--port", type=int, default=None, help=t("cli.help.web_port"))
    p_web.add_argument("--host", default=None, help=t("cli.help.web_host"))

    return parser


def main():
    # --lang applies to every message of this run, including translated --help
    lang = argv_lang(sys.argv[1:])
    if lang:
        os.environ["AGENTS_LANG"] = lang

    parser = build_parser()
    if len(sys.argv) == 1:
        # Default to list if no arguments passed
        manager = AgentManager()
        cmd_list(manager, None)
        return

    args = parser.parse_args()
    manager = AgentManager()

    cmd = args.command
    if cmd in ("list", "ls", "ps"):
        cmd_list(manager, args)
    elif cmd == "status":
        cmd_status(manager, args)
    elif cmd == "lang":
        cmd_lang(manager, args)
    elif cmd == "start":
        cmd_start(manager, args)
    elif cmd == "stop":
        cmd_stop(manager, args)
    elif cmd == "restart":
        cmd_restart(manager, args)
    elif cmd == "logs":
        cmd_logs(manager, args)
    elif cmd == "open":
        cmd_open(manager, args)
    elif cmd == "run":
        cmd_run(manager, args)
    elif cmd in ("scan", "discover"):
        cmd_scan(manager, args)
    elif cmd == "add":
        cmd_add(manager, args)
    elif cmd in ("remove", "rm", "delete"):
        cmd_remove(manager, args)
    elif cmd == "health":
        cmd_health(manager, args)
    elif cmd in ("web", "gui", "dashboard"):
        cmd_web(manager, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
