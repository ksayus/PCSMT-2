"""服务器注册表：saves/*.json 的列举、加载与补全。

替代旧版 ``Server.Get.List/Search`` 与 ``Examine.Server.InfoKeys``
（旧版读取时带写回副作用，这里拆成显式的 load / repair 两个操作）。
"""

from __future__ import annotations

import json
from pathlib import Path

from omniark.core import paths
from omniark.core.logger import get_logger
from omniark.exceptions import ServerNotFoundError
from omniark.models.server import ServerInstance, DATETIME_FORMAT
from omniark.utils.files import directory_size
from omniark.utils.formatting import human_readable_size
from omniark.utils.timeutil import detailed_time

logger = get_logger()

# 旧版字段名回退映射（数据兼容）
_LEGACY_KEY_MAP = {
    "Name": "server_name",
    "Counts": "start_count",
    "Core": "server_core",
    "Path": "server_path",
    "StartBatchPath": "server_start_batch_path",
    "Version": "server_version",
    "Size": "server_size",
}


def list_server_names(root: Path | None = None) -> list[str]:
    """列出所有已注册服务器名（跳过空文件与损坏的 JSON）。"""
    names: list[str] = []
    for file in sorted(paths.saves_dir(root).glob("*.json")):
        try:
            if file.stat().st_size == 0:
                logger.warning("服务器信息文件为空，跳过: %s", file)
                continue
            data = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("解析服务器信息文件失败 %s: %s", file, exc)
            continue
        name = data.get("Name") or data.get("server_name") or file.stem
        names.append(name)
    return names


def load_server(name: str, root: Path | None = None) -> ServerInstance:
    """加载服务器信息；不存在抛 ServerNotFoundError。"""
    return ServerInstance.load(name, root)


def repair_server_info(name: str, root: Path | None = None) -> ServerInstance:
    """加载并补全缺失字段（兼容旧版/旧键名），有改动时写回。

    对应旧版 ``Examine.Server.InfoKeys`` 的行为，但字段回退逻辑清晰无矛盾。
    """
    file = paths.server_save_file(name, root)
    if not file.exists():
        raise ServerNotFoundError(name)
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ServerNotFoundError(name)

    changed = False
    for new_key, old_key in _LEGACY_KEY_MAP.items():
        if new_key not in data:
            if old_key in data:
                data[new_key] = data[old_key]
            changed = True
    defaults = ServerInstance(Name=name).to_dict()
    for key, default in defaults.items():
        if key not in data or data[key] is None:
            data[key] = default
            changed = True

    server = ServerInstance.from_dict(data)

    # Size 缺失且目录存在时现场计算（旧版行为）
    if server.Size in ("", "N/A") and server.Path and Path(server.Path).is_dir():
        server.Size = human_readable_size(directory_size(server.Path))
        changed = True

    if changed:
        server.save(root)
    return server


def save_server(server: ServerInstance, root: Path | None = None) -> None:
    server.save(root)


def server_exists(name: str, root: Path | None = None) -> bool:
    return paths.server_save_file(name, root).exists()


def remove_server_record(name: str, root: Path | None = None) -> None:
    paths.server_save_file(name, root).unlink(missing_ok=True)
    paths.storage_size_file(name, root).unlink(missing_ok=True)
