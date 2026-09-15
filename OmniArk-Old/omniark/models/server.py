"""服务器实例数据模型。

与旧版 ``saves/<name>.json`` 的字段完全兼容（Name/Counts/Core/Path/
StartBatchPath/Size/Version/LatestStartedTime/CoreType），保证数据迁移零成本。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Any

from omniark.core import paths
from omniark.exceptions import ServerNotFoundError

DATETIME_FORMAT = "%Y/%m/%d/%H:%M:%S"  # 旧版时间格式，保持兼容


@dataclass
class ServerInstance:
    """一个 Minecraft 服务器实例的注册信息。"""

    Name: str
    Counts: int = 0                       # 累计启动次数
    Core: str = ""                        # 核心 jar 绝对路径
    Path: str = ""                        # 服务器目录绝对路径
    StartBatchPath: str = ""              # start.bat 绝对路径
    Size: str = ""                        # 如 "54.89MB"
    Version: str = ""                     # Minecraft 版本
    LatestStartedTime: str = ""           # DATETIME_FORMAT 格式
    CoreType: str = "official"            # official/forge/fabric/mohist

    # ------------------------------------------------------------ 序列化

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServerInstance":
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    # ------------------------------------------------------------ 持久化

    @classmethod
    def load(cls, name: str, root: Path | None = None) -> "ServerInstance":
        file = paths.server_save_file(name, root)
        if not file.exists():
            raise ServerNotFoundError(name)
        data = json.loads(file.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    def save(self, root: Path | None = None) -> None:
        file = paths.server_save_file(self.Name, root)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(
            json.dumps(self.to_dict(), indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    def delete_save(self, root: Path | None = None) -> None:
        file = paths.server_save_file(self.Name, root)
        file.unlink(missing_ok=True)

    # ------------------------------------------------------------ 便捷属性

    @property
    def directory(self) -> Path:
        return Path(self.Path)

    @property
    def core_file(self) -> Path:
        return Path(self.Core)

    @property
    def properties_file(self) -> Path:
        return self.directory / paths.Files.SERVER_PROPERTIES

    @property
    def eula_file(self) -> Path:
        return self.directory / paths.Files.EULA

    @property
    def mods_dir(self) -> Path:
        return self.directory / paths.Dirs.MODS

    @property
    def plugins_dir(self) -> Path:
        return self.directory / paths.Dirs.PLUGINS

    def exists(self) -> bool:
        """服务器目录是否真实存在于磁盘。"""
        return bool(self.Path) and self.directory.is_dir()
