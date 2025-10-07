# -*- coding: utf-8 -*-
"""
Сбор системной информации + локальный и публичный IP.
- Работает на Linux/macOS/Windows (Python 3.8+).
- Без зависимостей (urllib/socket). Опционально использует psutil, если установлен.
- Аккуратно оборачивает всё в try/except, чтобы не падать в "жёстких" окружениях.
"""

from __future__ import annotations
import json
import os
import platform
from pprint import pformat
import shutil
import socket
import subprocess
import sys
import time
from typing import Any, Dict, Optional

import psutil

def _bytes_to_human(n: int | None) -> str:
    """Перевод байт в человеко-читаемый формат."""
    try:
        if n is None:
            return "—"
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        f = float(n)
        while f >= 1024 and i < len(units) - 1:
            f /= 1024.0
            i += 1
        return f"{f:.2f} {units[i]}"
    except Exception:
        return str(n)

def _percent(v: Any) -> str:
    try:
        return f"{float(v):.2f}%"
    except Exception:
        return "—"

def _safe(func, default=None):
    """Вспомогательная обёртка: не даём вылетать наружу."""
    try:
        return func()
    except Exception:
        return default


def _get_python_info() -> Dict[str, Any]:
    return {
        "version": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
    }


def _get_os_info() -> Dict[str, Any]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
        "arch": platform.architecture()[0],
    }


def _get_cpu_info() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "logical_cores": _safe(lambda: os.cpu_count(), None),
    }
    if hasattr(os, "getloadavg"):
        info["loadavg_1_5_15"] = _safe(lambda: os.getloadavg(), None)

    if psutil:
        info["physical_cores"] = _safe(lambda: psutil.cpu_count(logical=False), None)
        info["freq_mhz"] = _safe(lambda: (psutil.cpu_freq().current if psutil.cpu_freq() else None), None)
        info["usage_percent_per_cpu"] = _safe(lambda: psutil.cpu_percent(percpu=True, interval=0.2), None)
    return info


def _get_memory_info() -> Dict[str, Any]:
    # Предпочтительно psutil → иначе пытаемся sysconf/ctypes
    if psutil:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        return {
            "total": vm.total,
            "available": vm.available,
            "used": vm.used,
            "percent": vm.percent,
            "swap_total": sm.total,
            "swap_used": sm.used,
            "swap_percent": sm.percent,
        }

    info: Dict[str, Any] = {}

    if sys.platform != "win32" and hasattr(os, "sysconf"):
        # Примерно для Unix
        pagesize = _safe(lambda: os.sysconf("SC_PAGE_SIZE"), 4096) or 4096
        phys_pages = _safe(lambda: os.sysconf("SC_PHYS_PAGES"), None)
        avail_pages = _safe(lambda: os.sysconf("SC_AVPHYS_PAGES"), None)
        if phys_pages is not None:
            info["total"] = phys_pages * pagesize
        if avail_pages is not None:
            info["available"] = avail_pages * pagesize

    if sys.platform == "win32":
        # Небольшой трюк через wmic (без сторонних модулей)
        def _wmic_total():
            out = subprocess.check_output(
                ["wmic", "OS", "get", "TotalVisibleMemorySize", "/Value"],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            ).decode(errors="ignore")
            for line in out.splitlines():
                if line.startswith("TotalVisibleMemorySize="):
                    return int(line.split("=", 1)[1]) * 1024  # KB → B
        def _wmic_free():
            out = subprocess.check_output(
                ["wmic", "OS", "get", "FreePhysicalMemory", "/Value"],
                creationflags=0x08000000,
            ).decode(errors="ignore")
            for line in out.splitlines():
                if line.startswith("FreePhysicalMemory="):
                    return int(line.split("=", 1)[1]) * 1024
        info["total"] = _safe(_wmic_total, None)
        info["available"] = _safe(_wmic_free, None)

    # Производные
    total = info.get("total")
    avail = info.get("available")
    if total is not None and avail is not None:
        used = max(0, total - avail)
        info["used"] = used
        info["percent"] = round((used / total) * 100, 2) if total else None
    return info


def _get_disk_info() -> Dict[str, Any]:
    # Основной раздел + список всех точек монтирования (если есть psutil)
    data: Dict[str, Any] = {}
    data["root"] = _safe(lambda: _disk_usage("/"), None)
    if psutil:
        parts = _safe(lambda: psutil.disk_partitions(all=False), [])
        mounts = []
        for p in parts or []:
            mounts.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "opts": p.opts,
                "usage": _safe(lambda p=p: _disk_usage(p.mountpoint), None),
            })
        data["mounts"] = mounts
    return data


def _disk_usage(path: str) -> Dict[str, Any]:
    du = shutil.disk_usage(path)
    used = du.total - du.free
    percent = round((used / du.total) * 100, 2) if du.total else None
    return {"total": du.total, "used": used, "free": du.free, "percent": percent}


def _get_hostname() -> str:
    return _safe(socket.gethostname, "") or ""


def _get_local_ip_primary() -> Optional[str]:
    """
    Даёт локальный IPv4 «выходящего» интерфейса.
    Метод: "виртуальное" подключение к 8.8.8.8:80 без отправки трафика.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _get_all_local_ips() -> Dict[str, Any]:
    ips = {"primary": _get_local_ip_primary(), "all": []}
    try:
        host = socket.gethostname()
        # getaddrinfo выдаст и v4, и v6
        addrs = socket.getaddrinfo(host, None)
        unique = []
        for fam, _, _, _, sockaddr in addrs:
            ip = sockaddr[0]
            if ip not in unique:
                unique.append(ip)
        ips["all"] = unique
    except Exception:
        pass

    if psutil:
        by_iface = {}
        try:
            for ifname, addrs in (psutil.net_if_addrs() or {}).items():
                lst = []
                for a in addrs:
                    if a.family in (socket.AF_INET, socket.AF_INET6):
                        lst.append(a.address)
                if lst:
                    by_iface[ifname] = lst
            ips["by_interface"] = by_iface
        except Exception:
            pass
    return ips


def _get_public_ip(timeout: float = 2.5) -> Optional[str]:
    """
    Публичный IP с авто-повторами по нескольким HTTP-сервисам.
    Без requests — используем urllib.
    """
    import urllib.request

    endpoints = [
        "https://api.ipify.org",           # простой текст
        "https://ifconfig.me/ip",          # простой текст
        "https://ipv4.icanhazip.com",      # простой текст
        "https://checkip.amazonaws.com",   # простой текст
    ]
    for url in endpoints:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read().decode("utf-8", errors="ignore").strip()
                if data:
                    return data
        except Exception:
            continue
    return None


def get_system_info(include_processes: bool = False) -> Dict[str, Any]:
    """
    Возвращает словарь с системной информацией и IP-адресами.
    :param include_processes: если True и установлен psutil — добавит топ-процессы по памяти/CPU.
    """
    info: Dict[str, Any] = {
        "timestamp": int(time.time()),
        "hostname": _get_hostname(),
        "python": _get_python_info(),
        "os": _get_os_info(),
        "cpu": _get_cpu_info(),
        "memory": _get_memory_info(),
        "disk": _get_disk_info(),
        "network": _get_all_local_ips(),
        "public_ip": _get_public_ip(),
    }

    if include_processes and psutil:
        # ТОП по памяти и CPU (по 5 штук), безопасно
        def top_by_memory(n=5):
            res = []
            for p in psutil.process_iter(attrs=["pid", "name", "username", "memory_info", "cpu_percent"]):
                try:
                    mi = p.info.get("memory_info")
                    res.append({
                        "pid": p.info.get("pid"),
                        "name": p.info.get("name"),
                        "user": p.info.get("username"),
                        "rss": getattr(mi, "rss", None) if mi else None,
                        "cpu_percent": p.info.get("cpu_percent"),
                    })
                except Exception:
                    continue
            res.sort(key=lambda x: (x["rss"] or 0), reverse=True)
            return res[:n]

        def top_by_cpu(n=5):
            # Небольшой прогрев для корректных процентов
            for p in psutil.process_iter():
                _ = _safe(lambda p=p: p.cpu_percent(None), 0)
            time.sleep(0.2)
            res = []
            for p in psutil.process_iter(attrs=["pid", "name", "username"]):
                try:
                    res.append({
                        "pid": p.info.get("pid"),
                        "name": p.info.get("name"),
                        "user": p.info.get("username"),
                        "cpu_percent": p.cpu_percent(None),
                    })
                except Exception:
                    continue
            res.sort(key=lambda x: (x["cpu_percent"] or 0), reverse=True)
            return res[:n]

        info["processes"] = {
            "top_memory": _safe(lambda: top_by_memory(5), []),
            "top_cpu": _safe(lambda: top_by_cpu(5), []),
        }

    return info

def _fmt_info(info: Dict[str, Any]) -> str:
    """Собрать красивый HTML из словаря get_system_info()."""
    try:
        host = info.get("hostname") or "—"
        py = info.get("python", {})
        os_ = info.get("os", {})
        cpu = info.get("cpu", {})
        mem = info.get("memory", {})
        disk = info.get("disk", {})
        net = info.get("network", {})
        pub_ip = info.get("public_ip") or "—"

        # ОС/Питон/Хост
        parts = []
        parts.append(
            "🖥 <b>Система</b>\n"
            f"• <b>Хост:</b> <code>{host}</code>\n"
            f"• <b>OS:</b> {os_.get('system','—')} {os_.get('release','')} ({os_.get('arch','')})\n"
            f"• <b>Версия:</b> <code>{os_.get('version','—')}</code>\n"
            f"• <b>Платформа:</b> <code>{os_.get('platform','—')}</code>\n"
            f"• <b>Python:</b> {py.get('implementation','—')} {py.get('version','—')}\n"
        )

        # CPU
        parts.append(
            "\n🧠 <b>CPU</b>\n"
            f"• <b>Логич. ядра:</b> {cpu.get('logical_cores','—')}\n"
            f"• <b>Физич. ядра:</b> {cpu.get('physical_cores','—')}\n"
            f"• <b>Частота:</b> {cpu.get('freq_mhz','—')} MHz\n"
            f"• <b>LoadAvg(1/5/15):</b> {cpu.get('loadavg_1_5_15','—')}\n"
        )

        # Память
        parts.append(
            "\n💾 <b>Память</b>\n"
            f"• <b>Total:</b> {_bytes_to_human(mem.get('total'))}\n"
            f"• <b>Used:</b>  {_bytes_to_human(mem.get('used'))} ({_percent(mem.get('percent'))})\n"
            f"• <b>Avail:</b> {_bytes_to_human(mem.get('available'))}\n"
            f"• <b>Swap:</b>  {_bytes_to_human(mem.get('swap_used'))} / {_bytes_to_human(mem.get('swap_total'))} ({_percent(mem.get('swap_percent'))})\n"
        )

        # Диск
        root = (disk or {}).get("root") or {}
        parts.append(
            "\n🗄 <b>Диск</b>\n"
            f"• <b>Root /:</b> {_bytes_to_human(root.get('used'))} / {_bytes_to_human(root.get('total'))} ({_percent(root.get('percent'))})\n"
        )
        mounts = (disk or {}).get("mounts") or []
        if mounts:
            parts.append("• <b>Точки монтирования:</b>\n")
            for m in mounts[:10]:  # не раздуваем
                u = m.get("usage") or {}
                parts.append(
                    f"  — <code>{m.get('mountpoint','?')}</code>: {_bytes_to_human(u.get('used'))}"
                    f" / {_bytes_to_human(u.get('total'))} ({_percent(u.get('percent'))})\n"
                )
            if len(mounts) > 10:
                parts.append(f"  … и ещё {len(mounts) - 10}\n")

        # Сеть / IP
        primary = (net or {}).get("primary") or "—"
        all_ips = (net or {}).get("all") or []
        by_iface = (net or {}).get("by_interface") or {}
        parts.append(
            "\n🌐 <b>Сеть</b>\n"
            f"• <b>Public IP:</b> <code>{pub_ip}</code>\n"
            f"• <b>Local (primary):</b> <code>{primary}</code>\n"
        )
        if all_ips:
            # ограничим вывод
            shown = ", ".join(f"<code>{ip}</code>" for ip in all_ips[:6])
            tail = f" … (+{len(all_ips)-6})" if len(all_ips) > 6 else ""
            parts.append(f"• <b>Все адреса:</b> {shown}{tail}\n")
        if by_iface:
            parts.append("• <b>Интерфейсы:</b>\n")
            cnt = 0
            for name, addrs in by_iface.items():
                cnt += 1
                if cnt > 6:
                    parts.append("  … (сокращено)\n")
                    break
                a = ", ".join(f"<code>{x}</code>" for x in addrs[:4])
                more = f" … (+{len(addrs)-4})" if len(addrs) > 4 else ""
                parts.append(f"  — <b>{name}</b>: {a}{more}\n")

        # Топ процессов (если есть)
        procs = info.get("processes") or {}
        top_mem = procs.get("top_memory") or []
        top_cpu = procs.get("top_cpu") or []
        if top_mem or top_cpu:
            parts.append("\n📊 <b>Процессы</b>\n")
        if top_mem:
            parts.append("• <b>Топ по памяти:</b>\n")
            for p in top_mem[:5]:
                parts.append(
                    f"  — <code>{p.get('pid')}</code> {p.get('name','?')} "
                    f"({p.get('user','?')}), RSS={_bytes_to_human(p.get('rss'))}, CPU={_percent(p.get('cpu_percent'))}\n"
                )
        if top_cpu:
            parts.append("• <b>Топ по CPU:</b>\n")
            for p in top_cpu[:5]:
                parts.append(
                    f"  — <code>{p.get('pid')}</code> {p.get('name','?')} "
                    f"({p.get('user','?')}), CPU={_percent(p.get('cpu_percent'))}\n"
                )

        return "".join(parts).strip()
    except Exception:
        # На всякий случай отдаём JSON как есть
        return f"<pre>{pformat(info)}</pre>"