"""Auto-discovery of micro-applications and agents on the host system."""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import EXCLUDED_AGENT_IDS

HOME = Path.home()


def _clean_markup(text: str) -> str:
    """Strip inline HTML and markdown syntax, leaving plain text."""
    text = re.sub(r'<!--.*?-->', ' ', text)
    text = re.sub(r'<[^>]*>', ' ', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)         # images
    text = re.sub(r'\[\s*\]\([^)]*\)', '', text)               # links left empty by image removal
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)       # [label](url) -> label
    text = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', text)       # [label][ref] -> label
    text = re.sub(r'\*\*|__|`|(?<!\w)\*|\*(?!\w)', '', text)  # emphasis / inline code
    return re.sub(r'\s+', ' ', text).strip()


def _shorten(text: str, limit: int = 120) -> str:
    """Cut text at a word boundary and add an ellipsis if it was truncated."""
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-—")
    return (cut or text[:limit]) + "…"


def extract_readme_info(dir_path: Path) -> Dict[str, str]:
    """Extract name and summary description from README.md if present."""
    readme_candidates = [dir_path / "README.md", dir_path / "readme.md", dir_path / "README"]
    for rm in readme_candidates:
        if rm.exists():
            try:
                text = rm.read_text(encoding="utf-8", errors="ignore")
                lines = text.splitlines()
                title = ""
                desc = ""
                in_fence = False
                # Some READMEs keep the real title in an HTML <h1> (centered logo blocks)
                m_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.IGNORECASE | re.DOTALL)
                html_title = _clean_markup(m_h1.group(1)) if m_h1 else ""
                for line in lines:
                    line = line.strip()
                    if line.startswith("```"):
                        in_fence = not in_fence
                        continue
                    if in_fence or not line:
                        continue
                    if line.startswith("# ") and not title:
                        title = _clean_markup(line.lstrip("# "))
                        # Remove leading icons/emojis if desirable or keep
                        title = re.sub(r'^[^\w\s]+', '', title).strip()
                        if not re.match(r'\w{2}', title):
                            title = ""
                    elif not line.startswith(("#", "---", "===", ">", "|", "<!--")) and not desc:
                        candidate = _shorten(_clean_markup(line))
                        if candidate and candidate not in (title, html_title):
                            desc = candidate
                            if (title or html_title) and desc:
                                break
                return {"title": title or html_title, "desc": desc}
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

    # 2. Check python files (app.py, config.py, server.py, app/server.py)
    cand_py_files = [
        dir_path / "app.py",
        dir_path / "server.py",
        dir_path / "config.py",
        dir_path / "main.py",
        dir_path / "app" / "server.py",
        dir_path / "app" / "config.py",
        dir_path / "app" / "app.py"
    ]
    for py_file in cand_py_files:
        if py_file.exists():
            try:
                text = py_file.read_text(errors="ignore")
                m = re.search(r'port\s*=\s*(?:int\(.*?)?(\d{2,5})', text, re.IGNORECASE)
                if m:
                    return int(m.group(1))
            except Exception:
                pass

    # 3. Check shell scripts (*.sh, run.sh)
    for sh_file in dir_path.glob("*.sh"):
        try:
            text = sh_file.read_text(errors="ignore")
            m = re.search(r'(?:PORT\s*=\s*["\']?|localhost:|127\.0\.0\.1:|:)(\d{4,5})', text, re.IGNORECASE)
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
            subdirs = [p for p in base_path.iterdir() if p.is_dir() and not p.name.startswith(".")]
        except Exception:
            continue

        for p in subdirs:
            if str(p) in seen_dirs:
                continue

            # Check if this directory is a micro-application
            has_app_py = (p / "app.py").exists() or (p / "server.py").exists() or (p / "main.py").exists()
            has_sub_app = (p / "app" / "server.py").exists() or (p / "app" / "app.py").exists()
            has_run_sh = (p / "run.sh").exists()
            sh_scripts = [f for f in p.glob("*.sh") if not f.name.startswith(".")]
            has_cli_py = (p / "cli.py").exists()
            has_package_json = (p / "package.json").exists()

            if not (has_app_py or has_sub_app or has_run_sh or sh_scripts or has_cli_py or has_package_json):
                # Check 1 level deeper (e.g. 2026/AI, 2026/corpo)
                try:
                    deeper = [d for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")]
                    for deep_p in deeper:
                        if str(deep_p) in seen_dirs:
                            continue
                        d_app = (deep_p / "app.py").exists() or (deep_p / "server.py").exists()
                        d_sub = (deep_p / "app" / "server.py").exists() or (deep_p / "app" / "app.py").exists()
                        d_run = (deep_p / "run.sh").exists()
                        d_sh = [f for f in deep_p.glob("*.sh") if not f.name.startswith(".")]
                        d_cli = (deep_p / "cli.py").exists()
                        if d_app or d_sub or d_run or d_sh or d_cli:
                            cand = _analyze_candidate(deep_p, d_app or d_sub, d_run or bool(d_sh), d_cli, d_sh)
                            if cand:
                                seen_dirs.add(str(deep_p))
                                results.append(cand)
                except Exception:
                    pass
                continue

            cand = _analyze_candidate(p, has_app_py or has_sub_app, has_run_sh or bool(sh_scripts), has_cli_py, sh_scripts)
            if cand:
                seen_dirs.add(str(p))
                results.append(cand)

    return results


def _analyze_candidate(p: Path, has_app: bool, has_run: bool, has_cli: bool, sh_scripts: Optional[List[Path]] = None) -> Optional[Dict[str, Any]]:
    readme = extract_readme_info(p)
    port = extract_port_from_project(p)
    venv = detect_venv(p)

    agent_id = re.sub(r'[^a-zA-Z0-9_\-]', '-', p.name.lower())
    name = readme["title"] or p.name.replace("_", " ").title()
    desc = readme["desc"] or f"Micro-application in {p.name}"

    # If launcher script exists (e.g. "Запустить Идейный Поиск МК.sh")
    start_cmd = None
    if sh_scripts:
        # Prefer script with 'запуск' or 'run' or 'start'
        launch_sh = next((s for s in sh_scripts if any(w in s.name.lower() for w in ["запуск", "run", "start"])), sh_scripts[0])
        start_cmd = f"bash '{launch_sh}'"
        clean_title = re.sub(r'^(Запустить|Run|Start)\s*', '', launch_sh.stem, flags=re.IGNORECASE).strip()
        if clean_title and (not readme["title"] or readme["title"] == p.name):
            name = clean_title
    elif (p / "run.sh").exists():
        start_cmd = str(p / "run.sh")
    elif (p / "app" / "server.py").exists():
        start_cmd = f"uv run --with fastapi --with uvicorn --with pydantic python3 {p / 'app' / 'server.py'}"
    elif has_app:
        py_bin = f"{venv}/bin/python" if venv else "python3"
        start_file = "app.py" if (p / "app.py").exists() else ("server.py" if (p / "server.py").exists() else "main.py")
        start_cmd = f"{py_bin} {start_file}"

    cat = "web_app" if (port or has_app) else ("cli_tool" if has_cli else "daemon")
    app_type = "daemon" if (has_app or has_run or start_cmd) else "cli"

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


def _norm_id(value: Optional[str]) -> str:
    """Id without case and separators, so `example-service` and `example-service` compare equal."""
    return re.sub(r'[^a-z0-9]', '', (value or "").lower())


def _norm_path(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return os.path.realpath(os.path.expanduser(value))


def find_registered_match(candidate: Dict[str, Any], registered: List[Any]) -> Optional[str]:
    """Return the id of the registered agent that this candidate is a duplicate of, if any.

    One app is often discovered several ways (project folder, systemd unit) under different ids,
    so the id alone is not enough. Signals, strongest first: same id, same systemd unit,
    same working directory, same id ignoring case and `-`/`_`.
    Ports are deliberately not used: they are guessed from scripts and shared by unrelated apps,
    so a port match could hide a genuinely new app.
    """
    cand_id = candidate["id"]
    cand_key = _norm_id(cand_id)
    cand_unit = candidate.get("systemd_unit")
    cand_dir = _norm_path(candidate.get("working_dir"))

    checks = (
        lambda a: a.id == cand_id,
        lambda a: bool(cand_unit) and a.systemd_unit == cand_unit,
        lambda a: bool(cand_dir) and _norm_path(a.working_dir) == cand_dir,
        lambda a: bool(cand_key) and _norm_id(a.id) == cand_key,
    )
    for check in checks:
        for agent in registered:
            if check(agent):
                return agent.id
    return None


def discover_all(scan_dirs: List[str], registered: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
    """Combine filesystem scans and systemd units, marking which are already registered.

    `registered` is the list of Agent objects already in the registry. Each candidate gets
    `is_registered` and `registered_as` (the matching agent's id). When several candidates
    are the same registered app, a single row is kept, preferring the one with the exact id.
    """
    registered = registered or []

    candidates = scan_directories(scan_dirs) + scan_systemd_user_services()
    seen_ids = set()
    unique_candidates = []
    row_for_registered: Dict[str, Dict[str, Any]] = {}

    for c in candidates:
        cid = c["id"]
        if cid in EXCLUDED_AGENT_IDS or cid in seen_ids:
            continue
        seen_ids.add(cid)

        match = find_registered_match(c, registered)
        c["is_registered"] = match is not None
        c["registered_as"] = match

        if match is None:
            unique_candidates.append(c)
            continue

        kept = row_for_registered.get(match)
        if kept is None:
            row_for_registered[match] = c
            unique_candidates.append(c)
        elif cid == match and kept["id"] != match:
            unique_candidates[unique_candidates.index(kept)] = c
            row_for_registered[match] = c

    return unique_candidates
