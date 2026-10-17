"""Collect host health numbers for a small status page. Standard library only."""

import os
import shutil
import socket
import subprocess


def parse_meminfo(text: str) -> dict:
    """Return total and available memory in bytes from /proc/meminfo text."""
    values = {}
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        parts = rest.split()
        if parts and parts[0].isdigit():
            values[key] = int(parts[0]) * 1024
    if "MemTotal" not in values:
        raise ValueError("MemTotal missing from /proc/meminfo")
    # MemAvailable needs kernel 3.14 or newer. Older kernels fall back to MemFree.
    available = values.get("MemAvailable", values.get("MemFree", 0))
    return {"total": values["MemTotal"], "available": available}


def parse_uptime(text: str) -> float:
    """Return uptime in seconds from /proc/uptime text."""
    return float(text.split()[0])


def read_tmux_sessions() -> list:
    """Return tmux session names, or an empty list if tmux is absent or no server runs."""
    try:
        result = subprocess.run(
            ["tmux", "ls", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def collect_status() -> dict:
    """Gather the current host status as a plain dict."""
    with open("/proc/meminfo", encoding="utf-8") as f:
        memory = parse_meminfo(f.read())
    with open("/proc/uptime", encoding="utf-8") as f:
        uptime = parse_uptime(f.read())
    disk = shutil.disk_usage("/")
    load1, load5, load15 = os.getloadavg()
    return {
        "hostname": socket.gethostname(),
        "uptime_seconds": uptime,
        "load": {"1m": load1, "5m": load5, "15m": load15},
        "memory": memory,
        "disk": {"total": disk.total, "free": disk.free},
        "tmux_sessions": read_tmux_sessions(),
    }
