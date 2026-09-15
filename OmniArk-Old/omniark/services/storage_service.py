"""服务器存储占用统计与 Excel 报表导出。

替代旧版 ``bin/export/timer.py``（TimerStorageSizeUpdate）与
``bin/download/Download.py``（Excel 导出）。

修复的旧版 bug：
- 定时线程名匹配失效导致线程无限叠加（改为注册表管理 + 单例调度器）
- Auto_Time 在间隔恰好 60 秒时返回 None
- Excel 玩家列名 chr(67+i) 超过 23 人越界（改用 openpyxl get_column_letter）
- 存储历史 JSON 无限增长（增加上限截断）
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from omniark.core import paths
from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.models.server import ServerInstance
from omniark.utils.files import directory_size
from omniark.utils.formatting import human_readable_size
from omniark.utils.timeutil import storage_snapshot_time

logger = get_logger()

MAX_HISTORY_POINTS = 10000  # 存储历史点上限（防止 JSON 无限增长）


# ------------------------------------------------------------ 存储统计

def record_storage_size(server: ServerInstance,
                        root: Path | None = None) -> str:
    """记录一次服务器存储占用，返回可读大小字符串。

    同时更新 server_storage_size/<name>.json 历史与 saves/<name>.json 的 Size。
    """
    size_str = human_readable_size(directory_size(server.directory))
    interval = get_config().StorageSizeUpdateTime
    time_str = storage_snapshot_time(interval)

    file = paths.storage_size_file(server.Name, root)
    history = _load_history(file)
    # 与旧版一致：时间戳与上一条相同则跳过（避免重复记录）
    if history["time"] and history["time"][-1] == time_str:
        return size_str

    history["storage_size"].append(size_str)
    history["time"].append(time_str)
    # 截断过长的历史
    if len(history["time"]) > MAX_HISTORY_POINTS:
        history["storage_size"] = history["storage_size"][-MAX_HISTORY_POINTS:]
        history["time"] = history["time"][-MAX_HISTORY_POINTS:]
    file.write_text(json.dumps(history, indent=4, ensure_ascii=False),
                    encoding="utf-8")

    server.Size = size_str
    server.save(root)
    logger.debug("服务器 %s 存储占用: %s", server.Name, size_str)
    return size_str


def get_storage_history(server_name: str,
                        root: Path | None = None) -> dict[str, list[str]]:
    """读取存储历史 {'storage_size': [...], 'time': [...]}。"""
    return _load_history(paths.storage_size_file(server_name, root))


def _load_history(file: Path) -> dict[str, list[str]]:
    if file.exists():
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "storage_size" in data:
                return {"storage_size": list(data.get("storage_size", [])),
                        "time": list(data.get("time", []))}
        except json.JSONDecodeError:
            logger.warning("存储历史文件损坏，重建: %s", file)
    return {"storage_size": [], "time": []}


# ------------------------------------------------------------ 定时调度器

class StorageScheduler:
    """存储占用定时更新调度器（每服务器一个线程，可停止，替代旧版
    线程名匹配失效导致无限叠加的实现）。"""

    def __init__(self) -> None:
        self._threads: dict[str, threading.Thread] = {}
        self._stop_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def start(self, server: ServerInstance, root: Path | None = None) -> None:
        """为服务器启动（或重启）定时更新线程。"""
        with self._lock:
            self._stop_locked(server.Name)  # 已存在则先停掉旧的
            stop_event = threading.Event()
            thread = threading.Thread(
                target=self._loop,
                args=(server, stop_event, root),
                name=f"storage-timer-{server.Name}",
                daemon=True,
            )
            self._stop_events[server.Name] = stop_event
            self._threads[server.Name] = thread
            thread.start()
        logger.info("服务器 %s 的存储统计线程已启动", server.Name)

    def stop(self, server_name: str) -> None:
        with self._lock:
            self._stop_locked(server_name)

    def stop_all(self) -> None:
        with self._lock:
            for name in list(self._stop_events):
                self._stop_locked(name)

    def _stop_locked(self, server_name: str) -> None:
        event = self._stop_events.pop(server_name, None)
        if event:
            event.set()
        self._threads.pop(server_name, None)

    def _loop(self, server: ServerInstance, stop_event: threading.Event,
              root: Path | None) -> None:
        while not stop_event.is_set():
            interval = max(get_config().StorageSizeUpdateTime, 60)
            # 以 1 秒为粒度等待，可随时被 stop_event 中断
            if stop_event.wait(timeout=interval):
                break
            try:
                record_storage_size(server, root)
            except (OSError, json.JSONDecodeError) as exc:
                logger.error("更新服务器 %s 存储占用失败: %s", server.Name, exc)


scheduler = StorageScheduler()


# ------------------------------------------------------------ Excel 报表

def export_server_excel(server: ServerInstance,
                        extra: dict[str, Any] | None = None,
                        root: Path | None = None) -> Path:
    """导出单个服务器信息到 Excel，返回文件路径。

    :param extra: 可选附加数据，键支持：
        history_players / white_list / banned_players / current_players
    """
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter

    extra = extra or {}
    wb = Workbook()
    ws = wb.active
    ws.title = server.Name

    headers = ["服务器名称", "版本号", "核心类型", "上次启动时间", "启动次数",
               "存储占用", "历史玩家", "白名单玩家", "封禁玩家", "当前玩家"]
    for col, title in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=title)

    values = [server.Name, server.Version, server.CoreType,
              server.LatestStartedTime, server.Counts, server.Size]
    for col, value in enumerate(values, start=1):
        ws.cell(row=2, column=col, value=value)

    player_columns = {
        7: extra.get("history_players", []),
        8: extra.get("white_list", []),
        9: extra.get("banned_players", []),
        10: extra.get("current_players", []),
    }
    for col, players in player_columns.items():
        for row, player in enumerate(players, start=2):
            ws.cell(row=row, column=col, value=player)

    # 存储变化数据表
    ws2 = wb.create_sheet("存储变化数据")
    history = get_storage_history(server.Name, root)
    ws2.cell(row=1, column=1, value="存储占用")
    ws2.cell(row=1, column=2, value="时间")
    for row, (size, ts) in enumerate(
            zip(history["storage_size"], history["time"]), start=2):
        ws2.cell(row=row, column=1, value=size)
        ws2.cell(row=row, column=2, value=ts)

    _auto_fit(wb)
    dest = paths.excel_dir(root) / f"{server.Name}.xlsx"
    dest.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dest)
    logger.info("Excel 报表已生成: %s", dest)
    return dest


def export_all_servers_excel(servers: list[ServerInstance],
                             root: Path | None = None) -> Path:
    """导出所有服务器到一个多 sheet 的 Excel 文件。"""
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter  # noqa: F401（供 _auto_fit 用）

    wb = Workbook()
    wb.remove(wb.active)
    for server in servers:
        ws = wb.create_sheet(server.Name[:31])  # sheet 名最长 31 字符
        rows = [
            ("服务器名称", server.Name), ("版本号", server.Version),
            ("核心类型", server.CoreType),
            ("上次启动时间", server.LatestStartedTime),
            ("启动次数", server.Counts), ("存储占用", server.Size),
        ]
        for row, (key, value) in enumerate(rows, start=1):
            ws.cell(row=row, column=1, value=key)
            ws.cell(row=row, column=2, value=value)
        history = get_storage_history(server.Name, root)
        ws.cell(row=9, column=1, value="存储占用历史")
        ws.cell(row=9, column=2, value="时间")
        for row, (size, ts) in enumerate(
                zip(history["storage_size"], history["time"]), start=10):
            ws.cell(row=row, column=1, value=size)
            ws.cell(row=row, column=2, value=ts)

    if not servers:
        wb.create_sheet("空")
    _auto_fit(wb)
    dest = paths.excel_dir(root) / paths.Files.SERVER_INFO_EXCEL
    dest.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dest)
    logger.info("Excel 报表已生成: %s", dest)
    return dest


def _auto_fit(wb) -> None:
    """按内容字节长度自动调整各 sheet 列宽。"""
    from openpyxl.utils import get_column_letter
    for ws in wb.worksheets:
        for column_cells in ws.columns:
            max_len = 0
            col_idx = column_cells[0].column
            for cell in column_cells:
                if cell.value is not None:
                    byte_len = len(str(cell.value).encode("utf-8"))
                    max_len = max(max_len, byte_len)
            ws.column_dimensions[get_column_letter(col_idx)].width = \
                min(max_len + 4, 60)
