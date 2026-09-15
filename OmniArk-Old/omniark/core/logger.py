"""日志系统：控制台彩色输出 + 按日期分目录的文件日志。

替代旧版 ``bin/export/log.py``，基于标准 logging 模块实现。
日志目录结构：logs/<年>/<月>/<日>/<程序名>-<日>.log（与旧版兼容）。
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

from omniark import PROGRAM_NAME
from omniark.core import paths

_LOGGER_NAME = "omniark"

_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",     # 青
    logging.INFO: "\033[32m",      # 绿
    logging.WARNING: "\033[33m",   # 黄
    logging.ERROR: "\033[31m",     # 红
    logging.CRITICAL: "\033[35m",  # 紫
}
_RESET = "\033[0m"


class _ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        if color:
            return f"{color}{message}{_RESET}"
        return message


def _daily_log_file(root: Path | None = None) -> Path:
    now = datetime.now()
    log_dir = paths.logs_dir(root) / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    log_dir.mkdir(parents=True, exist_ok=True)
    # 与旧版一致：每次启动以 时-分-秒 新建日志文件
    return log_dir / f"{now.strftime('%H-%M-%S')}.log"


def setup_logger(level: int = logging.DEBUG,
                 console: bool = True) -> logging.Logger:
    """初始化控制台日志（幂等，不写文件，无磁盘副作用）。

    文件日志由 :func:`attach_file_handler` 在 bootstrap 初始化时挂载。
    """
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    datefmt = "%H:%M:%S"

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(_ColorFormatter(fmt, datefmt))
        logger.addHandler(console_handler)

    return logger


def attach_file_handler(root: Path | None = None) -> None:
    """挂载按日期分目录的文件日志（bootstrap 时调用一次，幂等）。"""
    logger = logging.getLogger(_LOGGER_NAME)
    if any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        return
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    try:
        file_handler = logging.FileHandler(
            _daily_log_file(root), encoding="utf-8")
    except OSError:
        # 日志文件不可写不应导致程序崩溃
        logger.warning("日志文件不可写，仅输出到控制台")
        return
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt, "%H:%M:%S"))
    logger.addHandler(file_handler)


def get_logger() -> logging.Logger:
    """获取全局 logger（未初始化时自动初始化为仅控制台输出）。"""
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        setup_logger()
    return logger
