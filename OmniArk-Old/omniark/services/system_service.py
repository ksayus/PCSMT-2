"""Windows 系统集成服务：开机自启、快捷方式、进程检测。

替代旧版 Program.Do.AddStartup/RemoveStartup/CreateShortCut、
IsProgramRunning.py。仅 Windows 可用；其他平台调用为无操作。
"""

from __future__ import annotations

import sys
from pathlib import Path

import psutil

from omniark.core.logger import get_logger

logger = get_logger()

_STARTUP_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def is_frozen() -> bool:
    """是否为 PyInstaller 打包的可执行文件。"""
    return bool(getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"))


def program_command() -> str:
    """返回启动本程序的命令（打包后为 exe 路径，源码运行为 python 解释器 + 入口）。"""
    if is_frozen():
        return str(Path(sys.executable).resolve())
    return f'"{sys.executable}" "{Path(sys.argv[0]).resolve()}"'


# ------------------------------------------------------------ 开机自启

def add_startup(name: str) -> bool:
    """注册开机自启（HKCU\\...\\Run）。仅 Windows。"""
    if sys.platform != "win32":
        logger.warning("开机自启仅支持 Windows")
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _STARTUP_REG_PATH,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, program_command())
        logger.info("已添加开机自启: %s", name)
        return True
    except OSError as exc:
        logger.error("添加开机自启失败: %s", exc)
        return False


def remove_startup(name: str) -> bool:
    """移除开机自启。"""
    if sys.platform != "win32":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _STARTUP_REG_PATH,
                            0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
        logger.info("已移除开机自启: %s", name)
        return True
    except FileNotFoundError:
        return True  # 本来就不存在，视为成功
    except OSError as exc:
        logger.error("移除开机自启失败: %s", exc)
        return False


def is_startup_registered(name: str) -> bool:
    if sys.platform != "win32":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _STARTUP_REG_PATH,
                            0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, name)
        return True
    except FileNotFoundError:
        return False


def _desktop_dir() -> Path:
    """桌面目录（优先读注册表，兼容 OneDrive 重定向的桌面）。"""
    import winreg
    try:
        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion"
                r"\Explorer\User Shell Folders", 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "Desktop")
            import os
            return Path(os.path.expandvars(value))
    except OSError:
        return Path.home() / "Desktop"


def _start_menu_dir() -> Path:
    import os
    return Path(os.environ.get("APPDATA",
                               str(Path.home() / "AppData/Roaming"))) / \
        r"Microsoft\Windows\Start Menu\Programs"


# ------------------------------------------------------------ 快捷方式

def create_shortcut(name: str, on_desktop: bool = True) -> bool:
    """在桌面/开始菜单创建快捷方式（仅 Windows）。"""
    if sys.platform != "win32":
        return False
    try:
        from win32com.client import Dispatch
    except ImportError:
        logger.error("创建快捷方式需要 pywin32")
        return False

    target = str(Path(sys.executable).resolve())
    arguments = "" if is_frozen() else f'"{Path(sys.argv[0]).resolve()}"'
    workdir = str(Path(sys.executable).resolve().parent) if is_frozen() \
        else str(Path.cwd())

    try:
        shell = Dispatch("WScript.Shell")
        location = _desktop_dir() if on_desktop else _start_menu_dir()
        link_path = str(Path(location) / f"{name}.lnk")
        shortcut = shell.CreateShortCut(link_path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = workdir
        shortcut.save()
        logger.info("快捷方式已创建: %s", link_path)
        return True
    except Exception as exc:  # COM 异常类型繁杂，统一收敛
        logger.error("创建快捷方式失败: %s", exc)
        return False


# ------------------------------------------------------------ 窗口进程

def kill_cmd_window_by_title(title_keyword: str,
                             process_name: str = "cmd.exe") -> bool:
    """结束标题包含关键字的 cmd 窗口进程（旧版 IsProgramRunning.Do.taskkill）。

    用于未启用 RCON 时停止服务器。仅 Windows。
    """
    if sys.platform != "win32":
        return False
    try:
        import win32gui
        import win32process
    except ImportError:
        logger.error("结束窗口进程需要 pywin32")
        return False

    killed = False
    keyword = title_keyword.lower()

    def _callback(hwnd, _extra):
        nonlocal killed
        if keyword in win32gui.GetWindowText(hwnd).lower():
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                if process_name.lower() in proc.name().lower():
                    proc.kill()
                    logger.info("已结束窗口进程: PID %d (%s)", pid,
                                win32gui.GetWindowText(hwnd))
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
                logger.error("结束进程失败 PID %d: %s", pid, exc)
        return True

    win32gui.EnumWindows(_callback, None)
    return killed


# ------------------------------------------------------------ 进程检测

def count_same_name_processes() -> int:
    """统计与当前进程同名的进程数量（含自身）。"""
    current = Path(sys.executable).name.lower() if is_frozen() \
        else Path(sys.argv[0]).name.lower()
    count = 0
    for pid in psutil.pids():
        try:
            proc = psutil.Process(pid)
            name = proc.name().lower()
            if is_frozen():
                if name == current:
                    count += 1
            else:
                cmdline = " ".join(proc.cmdline()).lower()
                if current in cmdline:
                    count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return count
