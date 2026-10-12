"""Auto-discovery of micro-applications and agents on the host system."""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

HOME = Path.home()


def extract_readme_info(dir_path: Path) -> Dict[str, str]:
    """Extract name and summary description from README.md if present."""
    readme_candidates = [dir_path / "README.md", dir_path / "readme.md", dir_path / "README"]
    for rm in readme_candidates:
        if rm.exists():
            try:
                lines = rm.read_text(encoding="utf-8", errors="ignore").splitlines()
                title = ""
                desc = ""
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("# ") and not title:
                        title = line.lstrip("# ").strip()
                        # Remove leading icons/emojis if desirable or keep
                        title = re.sub(r'^[^\w\s]+', '', title).strip()
                    elif not line.startswith("#") and not line.startswith("---") and not desc:
                        desc = line[:120].strip()
                        if title and desc:
                            break
                return {"title": title, "desc": desc}
            except Exception:
                pass
    return {"title": "", "desc": ""}


def extract_port_from_project(dir_path: Path) -> Optional[int]:
    """Attempt to detect port from .env, app.py, config.py, run.sh."""
    # 1. Check .env / .env.example
    for env_name in [".env", ".env.example"]:
        env_file = dir_path / env_name
        if env_file.exists():
            try:
                text = env_file.read_text(errors="ignore")
                m = re.search(r'PORT\s*=\s*["\']?(\d{2,5})["\']?', text, re.IGNORECASE)
                if m:
                    return int(m.group(1))
            except Exception:
                pass

    # 2. Check python files (app.py, config.py, server.py)
    for py_name in ["app.py", "server.py", "config.py", "main.py"]:
        py_file = dir_path / py_name
        if py_file.exists():
            try:
                text = py_file.read_text(errors="ignore")
                m = re.search(r'port\s*=\s*(?:int\(.*?)?(\d{2,5})', text, re.IGNORECASE)
                if m:
                    return int(m.group(1))
            except Exception:
                pass

    # 3. Check run.sh
    run_sh = dir_path / "run.sh"
    if run_sh.exists():
        try:
            text = run_sh.read_text(errors="ignore")
            m = re.search(r'PORT\s*=\s*["\']?(\d{2,5})["\']?', text, re.IGNORECASE)
            if m:
                return int(m.group(1))
        except Exception:
            pass

    return None


def detect_venv(dir_path: Path) -> Optional[str]:
    """Find virtualenv in project directory."""
    for venv_name in [".venv", "venv", "env"]:
        v = dir_path / venv_name
        if v.is_dir() and (v / "bin" / "python").exists():
            return str(v)
    return None


def scan_directories(base_dirs: List[str]) -> List[Dict[str, Any]]:
    """Scan base directories for potential micro-apps."""
    results = []
    seen_dirs = set()

    for base_str in base_dirs:
        base_path = Path(base_str).resolve()
        if not base_path.exists() or not base_path.is_dir():
            continue

        try:
            # Look up to depth 2
            subdirs = [p for p in base_path.iterdir() if p.is_dir() and not p.name.startswith(".")]
        except Exception:
            continue

        for p in subdirs:
            if str(p) in seen_dirs:
                continue

            # Check if this directory is a micro-application
            has_app_py = (p / "app.py").exists() or (p / "server.py").exists() or (p / "main.py").exists()
            has_run_sh = (p / "run.sh").exists()
            has_cli_py = (p / "cli.py").exists()
            has_package_json = (p / "package.json").exists()

            if not (has_app_py or has_run_sh or has_cli_py or has_package_json):
                # Check 1 level deeper (e.g. 2026/AI, 2026/corpo)
                try:
                    deeper = [d for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")]
                    for deep_p in deeper:
                        if str(deep_p) in seen_dirs:
                            continue
                        d_app = (deep_p / "app.py").exists() or (deep_p / "server.py").exists()
                        d_run = (deep_p / "run.sh").exists()
                        d_cli = (deep_p / "cli.py").exists()
                        if d_app or d_run or d_cli:
                            cand = _analyze_candidate(deep_p, d_app, d_run, d_cli)
                            if cand:
                                seen_dirs.add(str(deep_p))
                                results.append(cand)
                except Exception:
                    pass
                continue

            cand = _analyze_candidate(p, has_app_py, has_run_sh, has_cli_py)
            if cand:
                seen_dirs.add(str(p))
                results.append(cand)

    return results


def _analyze_candidate(p: Path, has_app: bool, has_run: bool, has_cli: bool) -> Optional[Dict[str, Any]]:
    readme = extract_readme_info(p)
    port = extract_port_from_project(p)
    venv = detect_venv(p)

    agent_id = re.sub(r'[^a-zA-Z0-9_\-]', '-', p.name.lower())
    name = readme["title"] or p.name.replace("_", " ").title()
    desc = readme["desc"] or f"Micro-application in {p.name}"

    cat = "web_app" if (port or has_app) else ("cli_tool" if has_cli else "daemon")
    app_type = "daemon" if (has_app or has_run) else "cli"

    start_cmd = None
    if has_run:
        start_cmd = str(p / "run.sh")
    elif has_app:
        py_bin = f"{venv}/bin/python" if venv else "python3"
        start_file = "app.py" if (p / "app.py").exists() else ("server.py" if (p / "server.py").exists() else "main.py")
        start_cmd = f"{py_bin} {start_file}"

    return {
        "id": agent_id,
        "name": name,
        "description": desc,
        "category": cat,
        "type": app_type,
        "working_dir": str(p),
        "start_cmd": start_cmd,
        "port": port,
        "url": f"http://localhost:{port}" if port else None,
        "venv_path": venv,
        "tags": [p.name.lower()]
    }


def scan_systemd_user_services() -> List[Dict[str, Any]]:
    """Scan user systemd units in ~/.config/systemd/user."""
    services = []
    user_systemd_dir = HOME / ".config" / "systemd" / "user"
    if not user_systemd_dir.exists():
        return services

    for unit_file in user_systemd_dir.glob("*.service"):
        try:
            text = unit_file.read_text(errors="ignore")
            desc = ""
            m_desc = re.search(r'Description=(.*)', text)
            if m_desc:
                desc = m_desc.group(1).strip()

            m_work = re.search(r'WorkingDirectory=(.*)', text)
            work_dir = m_work.group(1).strip() if m_work else None

            port = None
            m_port = re.search(r'PORT=(\d+)', text)
            if m_port:
                port = int(m_port.group(1))

            unit_name = unit_file.name
            agent_id = unit_file.stem.replace("_", "-")

            services.append({
                "id": agent_id,
                "name": desc or unit_file.stem.replace("_", " ").title(),
                "description": desc or f"Systemd user unit {unit_name}",
                "category": "web_app" if port else "system_service",
                "type": "systemd",
                "systemd_unit": unit_name,
                "systemd_user": True,
                "working_dir": work_dir,
                "port": port,
                "url": f"http://localhost:{port}" if port else None,
                "tags": ["systemd", unit_file.stem]
            })
        except Exception:
            pass

    return services


def discover_all(scan_dirs: List[str], registered_ids: Optional[set] = None) -> List[Dict[str, Any]]:
    """Combine filesystem scans and systemd units, marking which are already registered."""
    if registered_ids is None:
        registered_ids = set()

    candidates = scan_directories(scan_dirs) + scan_systemd_user_services()
    seen_ids = set()
    unique_candidates = []

    for c in candidates:
        cid = c["id"]
        if cid in seen_ids:
            continue
        seen_ids.add(cid)
        c["is_registered"] = (cid in registered_ids)
        unique_candidates.append(c)

    return unique_candidates
