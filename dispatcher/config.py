"""Configuration and persistent storage for Agent Dispatcher."""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "agent_dispatcher"
STATE_DIR = HOME / ".local" / "state" / "agent_dispatcher"
PIDS_DIR = STATE_DIR / "pids"
LOGS_DIR = STATE_DIR / "logs"
CONFIG_FILE = CONFIG_DIR / "agents.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "web_port": 8800,
    "web_host": "0.0.0.0",
    "theme": "dark",
    "scan_dirs": [
        str(HOME / "Projects"),
        str(HOME / "Downloads")
    ],
    "auto_refresh_sec": 3
}

DEFAULT_AGENTS: List[Dict[str, Any]] = []


def ensure_dirs():
    """Ensure all configuration and state directories exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PIDS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> Dict[str, Any]:
    """Load settings or return defaults."""
    ensure_dirs()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict[str, Any]):
    """Save settings to disk."""
    ensure_dirs()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def load_agents_config() -> List[Dict[str, Any]]:
    """Load agent configurations or initialize default."""
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                agents = json.load(f)
                if isinstance(agents, list):
                    return agents
        except Exception:
            pass

    # If first run, initialize with defaults
    save_agents_config(DEFAULT_AGENTS)
    return DEFAULT_AGENTS.copy()


def save_agents_config(agents: List[Dict[str, Any]]):
    """Save agents configuration to disk."""
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)
