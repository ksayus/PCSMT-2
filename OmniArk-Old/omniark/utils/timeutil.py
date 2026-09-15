"""时间工具（替代旧版 GetTime.py，去除模块加载时的静态时间缓存）。

旧版 ``Time.Now`` 在模块导入时取一次时间后就永远不变，是典型 bug；
这里全部改为函数调用，每次取当前时间。
"""

from __future__ import annotations

from datetime import datetime

DATETIME_FORMAT = "%Y/%m/%d/%H:%M:%S"


def now() -> datetime:
    return datetime.now()


def detailed_time() -> str:
    """``2020/01/01/00:00:00``（旧版 saves 时间格式）。"""
    return datetime.now().strftime(DATETIME_FORMAT)


def hour_minute_second() -> str:
    """``01-01-01``"""
    return datetime.now().strftime("%H-%M-%S")


def minute_second() -> str:
    return datetime.now().strftime("%M-%S")


def storage_snapshot_time(update_interval_seconds: int) -> str:
    """按存储统计更新间隔选择合适精度的时间串（旧版 Auto_Time 行为）。"""
    n = datetime.now()
    if update_interval_seconds < 60:
        return n.strftime("%Y年-%m月-%d日-%H时-%M分-%S秒")
    if update_interval_seconds < 3600:
        return n.strftime("%Y年-%m月-%d日-%H时-%M分")
    if update_interval_seconds < 86400:
        return n.strftime("%Y年-%m月-%d日-%H时")
    if update_interval_seconds < 604800:
        return n.strftime("%Y年-%m月-%d日")
    if update_interval_seconds < 2592000:
        return n.strftime("%Y年-%m月")
    return n.strftime("%Y年")
