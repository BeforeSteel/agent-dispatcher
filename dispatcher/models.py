"""Data models for agents and real-time status."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Agent:
    id: str
    name: str
    description: str = ""
    category: str = "web_app"  # web_app, daemon, cli_tool, cli_agent, system_service, docker, ai_agent
    type: str = "daemon"       # daemon, systemd, docker, cli
    working_dir: Optional[str] = None
    start_cmd: Optional[str] = None
    stop_cmd: Optional[str] = None
    restart_cmd: Optional[str] = None
    run_cmd: Optional[str] = None
    systemd_unit: Optional[str] = None
    systemd_user: bool = True
    container_name: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    pid_file: Optional[str] = None
    log_file: Optional[str] = None
    venv_path: Optional[str] = None
    health_endpoint: Optional[str] = None
    auto_start: bool = False
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    description_i18n: Optional[Dict[str, str]] = None
    name_i18n: Optional[Dict[str, str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentLiveStatus:
    id: str
    name: str
    category: str
    type: str
    status: str            # RUNNING, STOPPED, FAILED, READY, MISSING, UNKNOWN
    status_icon: str       # 🟢, ⚪, 🔴, ⚡, ❓
    is_running: bool = False
    pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    uptime: Optional[str] = None
    port: Optional[int] = None
    port_listening: bool = False
    urls: List[Dict[str, str]] = field(default_factory=list)  # [{"label": "Local", "url": "..."}]
    log_file: Optional[str] = None
    description: str = ""
    working_dir: Optional[str] = None
    error_message: Optional[str] = None
    description_i18n: Optional[Dict[str, str]] = None
    name_i18n: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
