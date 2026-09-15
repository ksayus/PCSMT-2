"""服务器进程管理器（替代旧版基于 cmd 窗口标题的进程查找）。

设计：
- 启动用 ``subprocess.Popen``，**不弹任何终端窗口**（Windows 下
  ``CREATE_NO_WINDOW``），进程句柄存入内存注册表；
- 进程 stdout/stderr 重定向到服务器目录 ``logs/console.log``（JVM 启动
  错误如 UnsupportedClassVersionError 也能查到；运行期日志 MC 自己会写
  ``logs/latest.log``）；
- PID 同时写入服务器目录 ``omniark.pid``，程序重启后仍能查询状态、
  结束进程（不再依赖窗口标题匹配这种脆弱手段）；
- 停止优先优雅方式（调用方先走 RCON /stop），兜底 ``taskkill /T``
  结束整棵进程树（cmd → java 子进程一起清理）。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import psutil

from omniark.core.logger import get_logger

logger = get_logger()

PID_FILENAME = "omniark.pid"
CONSOLE_LOG = Path("logs") / "console.log"

# 服务器名 -> Popen 句柄（仅本进程启动的服务器有句柄）
_processes: dict[str, subprocess.Popen] = {}
# 服务器名 -> console.log 文件句柄（随进程生命周期持有）
_log_handles: dict[str, object] = {}


# ------------------------------------------------------------ 启动

def start(name: str, command: list[str], cwd: str | Path) -> subprocess.Popen:
    """以子进程方式启动服务器并登记（无新终端窗口，输出进 console.log）。"""
    cwd = Path(cwd)
    log_file = cwd / CONSOLE_LOG
    log_file.parent.mkdir(parents=True, exist_ok=True)
    out = open(log_file, "a", encoding="utf-8", errors="ignore")
    kwargs: dict = {
        "cwd": str(cwd),
        "stdout": out,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        # 不创建任何可见窗口（CREATE_NEW_CONSOLE 会弹终端，禁用）
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    proc = subprocess.Popen(command, **kwargs)
    _processes[name] = proc
    _log_handles[name] = out
    _write_pid(cwd, proc.pid)
    logger.info("进程已启动: %s (pid=%d, 日志=%s)", name, proc.pid, log_file)
    return proc


# ------------------------------------------------------------ 状态

def pid_of(name: str, server_dir: str | Path | None = None) -> int | None:
    """获取服务器进程 PID（注册表句柄优先，其次 pid 文件）。"""
    proc = _processes.get(name)
    if proc is not None:
        if proc.poll() is None:
            return proc.pid
        # 句柄已退出，清理登记
        _release(name)
    if server_dir is not None:
        return _read_pid(Path(server_dir))
    return None


def is_running(name: str, server_dir: str | Path | None = None) -> bool:
    """进程是否存活（句柄或 PID 均检测）。"""
    pid = pid_of(name, server_dir)
    return pid is not None and _pid_alive(pid)


def _pid_alive(pid: int) -> bool:
    try:
        return psutil.pid_exists(pid)
    except Exception:  # psutil 异常时退化到 tasklist
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True, text=True, timeout=5)
        return str(pid) in (result.stdout or "")


def _release(name: str) -> None:
    """清理登记并关闭 console.log 文件句柄。"""
    _processes.pop(name, None)
    handle = _log_handles.pop(name, None)
    if handle is not None:
        try:
            handle.close()
        except OSError:
            pass


# ------------------------------------------------------------ 停止

def stop(name: str, server_dir: str | Path | None = None,
         timeout: float = 10.0) -> bool:
    """结束进程树（taskkill /T /F 兜底）。返回是否确认已结束。

    调用方应先尝试优雅停止（RCON /stop）再调用本函数兜底。
    """
    pid = pid_of(name, server_dir)
    if pid is None:
        _release(name)
        if server_dir:
            _remove_pid(Path(server_dir))
        return True
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True, timeout=timeout)
        else:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
    except (subprocess.TimeoutExpired, psutil.NoSuchProcess, OSError) as exc:
        logger.warning("结束进程 %s (pid=%d) 异常: %s", name, pid, exc)

    _release(name)
    if server_dir:
        _remove_pid(Path(server_dir))
    stopped = not _pid_alive(pid)
    if stopped:
        logger.info("进程已结束: %s (pid=%d)", name, pid)
    return stopped


def wait_exit(name: str, timeout: float = 15.0) -> bool:
    """等待本进程启动的服务器退出（RCON stop 后调用）。"""
    proc = _processes.get(name)
    if proc is None:
        return True
    try:
        proc.wait(timeout=timeout)
        _release(name)
        return True
    except subprocess.TimeoutExpired:
        return False


# ------------------------------------------------------------ PID 文件

def _write_pid(server_dir: Path, pid: int) -> None:
    try:
        (server_dir / PID_FILENAME).write_text(str(pid), encoding="utf-8")
    except OSError as exc:
        logger.warning("写入 PID 文件失败: %s", exc)


def _read_pid(server_dir: Path) -> int | None:
    file = server_dir / PID_FILENAME
    if not file.is_file():
        return None
    try:
        pid = int(file.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None
    # PID 可能已被系统复用，校验进程确实存在
    return pid if _pid_alive(pid) else None


def _remove_pid(server_dir: Path) -> None:
    try:
        (server_dir / PID_FILENAME).unlink(missing_ok=True)
    except OSError:
        pass
