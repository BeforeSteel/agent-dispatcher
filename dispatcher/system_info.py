"""System monitoring, network detection, and port utilities."""

import os
import time
import socket
import subprocess
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def format_uptime(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    rem_sec = seconds % 60
    if minutes < 60:
        return f"{minutes}m {rem_sec:02d}s"
    hours = minutes // 60
    rem_min = minutes % 60
    if hours < 24:
        return f"{hours}h {rem_min:02d}m"
    days = hours // 24
    rem_hours = hours % 24
    return f"{days}d {rem_hours}h"


def get_network_ips() -> Dict[str, str]:
    """Return dictionary of IP addresses by network type (LAN, Tailscale, etc.)."""
    ips = {"localhost": "127.0.0.1"}
    try:
        out = subprocess.check_output(["hostname", "-I"], stderr=subprocess.DEVNULL).decode().strip().split()
        for ip in out:
            if ip.startswith("127."):
                continue
            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                ips["lan"] = ip
            elif ip.startswith("100."):
                ips["tailscale"] = ip
            elif "other" not in ips:
                ips["other"] = ip
    except Exception:
        pass
    return ips


def get_network_urls(port: int) -> List[Dict[str, str]]:
    """Return formatted URLs for a given port."""
    if not port:
        return []
    urls = [{"label": "Localhost", "url": f"http://localhost:{port}"}]
    ips = get_network_ips()
    if "lan" in ips:
        urls.append({"label": f"LAN ({ips['lan']})", "url": f"http://{ips['lan']}:{port}"})
    if "tailscale" in ips:
        urls.append({"label": f"Tailscale ({ips['tailscale']})", "url": f"http://{ips['tailscale']}:{port}"})
    return urls


def is_port_in_use(port: int) -> bool:
    """Check if TCP port is currently listening."""
    if not port:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_pid_listening_on_port(port: int) -> Optional[int]:
    """Find PID listening on the given TCP port."""
    if not port:
        return None
    if HAS_PSUTIL:
        try:
            for conn in psutil.net_connections(kind="tcp"):
                if conn.laddr and conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    if conn.pid:
                        return conn.pid
        except Exception:
            pass
    # Fallback to fuser / lsof / ss
    try:
        out = subprocess.check_output(["fuser", f"{port}/tcp"], stderr=subprocess.DEVNULL).decode().strip()
        pids = [int(p) for p in out.split() if p.isdigit()]
        if pids:
            return pids[0]
    except Exception:
        pass
    return None


def get_gpu_stats() -> Optional[Dict[str, Any]]:
    """Query NVIDIA GPU metrics (Utilization, VRAM, Temperature, Power)."""
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit,name",
            "--format=csv,noheader,nounits"
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=1.5).decode().strip()
        if not out:
            return None
        parts = [p.strip() for p in out.split(",")]
        if len(parts) >= 4:
            gpu_util = int(parts[0])
            mem_used_mib = int(parts[1])
            mem_total_mib = int(parts[2])
            temp_c = int(parts[3])
            power_w = round(float(parts[4]), 1) if len(parts) > 4 and parts[4] else None
            power_limit_w = round(float(parts[5]), 1) if len(parts) > 5 and parts[5] else None
            name = parts[6] if len(parts) > 6 else "NVIDIA GPU"

            return {
                "available": True,
                "name": name,
                "gpu_util_percent": gpu_util,
                "mem_used_gb": round(mem_used_mib / 1024, 1),
                "mem_total_gb": round(mem_total_mib / 1024, 1),
                "mem_percent": round((mem_used_mib / mem_total_mib) * 100, 1),
                "temperature_c": temp_c,
                "power_w": power_w,
                "power_limit_w": power_limit_w
            }
    except Exception:
        pass
    return None


def get_system_stats() -> Dict[str, Any]:
    """Collect overall system health and resources."""
    stats: Dict[str, Any] = {
        "hostname": socket.gethostname(),
        "ips": get_network_ips(),
        "timestamp": time.time()
    }

    # GPU Stats
    gpu = get_gpu_stats()
    if gpu:
        stats["gpu"] = gpu

    if HAS_PSUTIL:
        try:
            stats["cpu_percent"] = psutil.cpu_percent(interval=None)
            stats["cpu_count"] = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            stats["memory_total_gb"] = round(mem.total / (1024 ** 3), 2)
            stats["memory_used_gb"] = round(mem.used / (1024 ** 3), 2)
            stats["memory_percent"] = mem.percent

            # Disks
            disks = {}
            disk_paths = dict.fromkeys(
                ["/"] + [partition.mountpoint for partition in psutil.disk_partitions()]
            )
            for path in disk_paths:
                if Path(path).exists():
                    try:
                        du = psutil.disk_usage(path)
                        disks[path] = {
                            "total_gb": round(du.total / (1024 ** 3), 1),
                            "free_gb": round(du.free / (1024 ** 3), 1),
                            "percent": du.percent
                        }
                    except Exception:
                        pass
            stats["disks"] = disks
        except Exception as e:
            stats["error"] = str(e)
    else:
        stats["cpu_percent"] = 0
        stats["memory_percent"] = 0

    return stats
