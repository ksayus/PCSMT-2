"""程序级管理：配置修改、清理/重置、资源占用、自更新重启。

替代旧版 ``bin/command/Program.py``。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import psutil

from omniark import PROGRAM_NAME, __release_channel__, __version__
from omniark.core import paths
from omniark.core.config import AppConfig, get_config, set_config
from omniark.core.logger import get_logger
from omniark.services import system_service

logger = get_logger()


# ------------------------------------------------------------ 配置修改

def update_config(**changes) -> AppConfig:
    """修改配置并写回 config.json（统一入口，替代 8 个 Change 函数）。"""
    cfg = get_config()
    cfg.update(**changes)
    cfg.save()
    set_config(cfg)
    logger.info("配置已更新: %s", {k: v for k, v in changes.items()
                                   if "password" not in k.lower()})
    return cfg


def reset_settings(root: Path | None = None) -> AppConfig:
    """重置为默认配置。"""
    cfg = AppConfig()
    cfg.save(paths.config_file(root))
    set_config(cfg)
    logger.info("配置已重置为默认值")
    return cfg


def set_auto_startup(enabled: bool) -> None:
    """修改开机自启（同时写配置与注册表）。"""
    update_config(AutomaticStartup=enabled)
    if enabled:
        system_service.add_startup(PROGRAM_NAME)
    else:
        system_service.remove_startup(PROGRAM_NAME)


# ------------------------------------------------------------ 清理 / 格式化

def clear_logs(root: Path | None = None) -> int:
    """清理非当日的日志目录，返回删除的目录数。"""
    root = root or paths.workspace_root()
    today = datetime.now()
    removed = 0
    logs = paths.logs_dir(root)
    if not logs.is_dir():
        return 0
    for year_dir in logs.iterdir():
        if not year_dir.is_dir():
            continue
        if year_dir.name != str(today.year):
            shutil.rmtree(year_dir, ignore_errors=True)
            removed += 1
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            if month_dir.name != f"{today.month:02d}":
                shutil.rmtree(month_dir, ignore_errors=True)
                removed += 1
                continue
            for day_dir in month_dir.iterdir():
                if day_dir.is_dir() and day_dir.name != f"{today.day:02d}":
                    shutil.rmtree(day_dir, ignore_errors=True)
                    removed += 1
    logger.info("日志清理完成，删除 %d 个目录", removed)
    return removed


def clear_latest_files(root: Path | None = None) -> None:
    """清空 latest.txt 与 resource/latest.json（修复旧版清错路径的 bug）。"""
    root = root or paths.workspace_root()
    for file in (root / paths.Files.LATEST_TXT,
                 paths.resource_dir(root) / paths.Files.LATEST_JSON):
        file.unlink(missing_ok=True)
    logger.info("latest 缓存已清空")


def format_program(root: Path | None = None) -> None:
    """格式化程序：清日志 + 清缓存 + 重置配置（服务器数据不动）。"""
    clear_logs(root)
    clear_latest_files(root)
    reset_settings(root)
    logger.warning("程序已格式化（服务器数据未受影响）")


# ------------------------------------------------------------ 资源占用

def cpu_usage() -> dict[str, float]:
    """CPU 占用率与频率（psutil，采样约 0.5 秒）。"""
    percent = psutil.cpu_percent(interval=0.5)
    freq = psutil.cpu_freq()
    return {
        "percent": percent,
        "freq_current": round(freq.current, 2) if freq else 0.0,
        "freq_max": round(freq.max, 2) if freq else 0.0,
    }


def ram_usage() -> dict[str, float]:
    """内存占用。"""
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_mb": round(mem.used / 1024 / 1024, 2),
        "total_mb": round(mem.total / 1024 / 1024, 2),
    }


def disk_usage(root: Path | None = None) -> dict[str, float]:
    """工作目录所在磁盘的占用（修复旧版盘符推导 bug）。"""
    root = root or paths.workspace_root()
    usage = shutil.disk_usage(root.anchor or str(root))
    total_gb = usage.total / 1024 ** 3
    free_gb = usage.free / 1024 ** 3
    used_gb = total_gb - free_gb
    return {
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
        "used_percent": round(used_gb / total_gb * 100, 2) if total_gb else 0.0,
        "free_percent": round(free_gb / total_gb * 100, 2) if total_gb else 0.0,
    }


def program_info() -> dict[str, str]:
    return {
        "name": PROGRAM_NAME,
        "version": f"{__version__}-{__release_channel__}",
        "python": sys.version.split()[0],
    }


# ------------------------------------------------------------ 自更新重启

def write_restart_script(new_program_name: str,
                         root: Path | None = None) -> Path:
    """生成 delete_old_program.bat（更新后删除旧版本并启动新版本）。

    保留旧版的 mshta 隐藏窗口技巧。
    """
    root = root or paths.workspace_root()
    old_exe = root / f"PCSMT2-v{__version__}.exe"
    content = (
        "@echo off\n"
        'if "%1" == "h" goto begin\n'
        'start mshta vbscript:createobject("wscript.shell").run("""%~nx0""h",0)(window.close)&&exit\n'
        ":begin\n"
        "timeout /t 5\n"
        f"cd {root}\n"
        f'powershell rm "{old_exe}"\n'
        f'start "" "{new_program_name}"\n'
        "exit\n"
    )
    script = root / paths.Files.DELETE_OLD_PROGRAM
    script.write_text(content, encoding="utf-8")
    return script


def restart_to_new_version(new_program_name: str,
                           root: Path | None = None) -> None:
    """执行更新重启（仅打包环境有意义）。"""
    root = root or paths.workspace_root()
    script = write_restart_script(new_program_name, root)
    subprocess.Popen(["cmd", "/c", str(script), "h"],
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    time.sleep(1)
    sys.exit(0)


def delete_restart_script(root: Path | None = None) -> None:
    (root or paths.workspace_root()).joinpath(
        paths.Files.DELETE_OLD_PROGRAM).unlink(missing_ok=True)
