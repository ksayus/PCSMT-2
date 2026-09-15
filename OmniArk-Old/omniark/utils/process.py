"""进程与系统命令封装（全面替代旧版的 os.system 调用）。

所有外部命令统一走 subprocess，参数以列表传递，杜绝 shell 注入。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from omniark.core.logger import get_logger

logger = get_logger()


def run(args: list[str], cwd: str | Path | None = None,
        timeout: int | None = None, capture: bool = True) -> subprocess.CompletedProcess:
    """同步执行命令并返回结果。失败抛 subprocess.CalledProcessError。"""
    logger.debug("执行命令: %s", " ".join(str(a) for a in args))
    return subprocess.run(
        [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
        capture_output=capture,
        text=True,
        check=True,
    )


def run_shell(args: list[str], cwd: str | Path | None = None) -> int:
    """同步执行命令，输出直接透传到控制台，返回退出码。"""
    logger.debug("执行命令: %s", " ".join(str(a) for a in args))
    return subprocess.call([str(a) for a in args],
                           cwd=str(cwd) if cwd else None)


def spawn_detached(args: list[str], cwd: str | Path | None = None) -> subprocess.Popen:
    """启动独立进程（不等待、不随本进程退出），用于启动 MC 服务器。"""
    logger.debug("启动进程: %s", " ".join(str(a) for a in args))
    creationflags = 0
    if sys.platform == "win32":
        creationflags = (subprocess.CREATE_NEW_CONSOLE
                         | subprocess.CREATE_NEW_PROCESS_GROUP)
    return subprocess.Popen(
        [str(a) for a in args],
        cwd=str(cwd) if cwd else None,
        creationflags=creationflags,
    )


def kill_by_pid(pid: int, force: bool = True) -> bool:
    """按 PID 结束进程（Windows taskkill / POSIX kill）。"""
    try:
        if sys.platform == "win32":
            args = ["taskkill", "/PID", str(pid)]
            if force:
                args.append("/F")
            subprocess.run(args, capture_output=True, check=True)
        else:
            import signal
            os_kill(pid, signal.SIGKILL if force else signal.SIGTERM)
        return True
    except (subprocess.CalledProcessError, OSError) as exc:
        logger.error("结束进程 %d 失败: %s", pid, exc)
        return False


def os_kill(pid: int, sig: int) -> None:
    import os
    os.kill(pid, sig)


def open_in_explorer(path: str | Path) -> None:
    """用系统默认方式打开文件/目录。"""
    path = Path(path)
    if sys.platform == "win32":
        # os.startfile 无注入风险（不走 shell）
        import os
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
