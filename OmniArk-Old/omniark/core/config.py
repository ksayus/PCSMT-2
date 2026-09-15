"""程序配置管理（读写 config.json，与旧版键名完全兼容）。

旧版 ``Info.Config`` 为每个键手写一个 classmethod，这里改为 dataclass +
映射表，新增配置项只需改一处。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, asdict
from pathlib import Path
from typing import Any

from omniark.core import paths
from omniark.exceptions import ConfigError


@dataclass
class AppConfig:
    """程序配置。字段默认值与旧版 ``Info.Config.Config`` 保持一致。"""

    PCSMT2_Version: str = "1.2.2.1.3"
    ReleaseVersion: str = "Release"
    RunningMemories_Min: int = 1024
    RunningMemories_Max: int = 2048
    Nogui: bool = True
    WaitEulaGenerateTime: int = 30
    AutomaticStartup: bool = True
    AutoUpdateSource: str = "Github"
    MinecraftTestVersion: bool = False
    StorageSizeUpdateTime: int = 3600
    Port: int = 5000

    # ------------------------------------------------------------ 序列化

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        """从字典构建，未知键忽略、缺失键用默认值、类型错误抛 ConfigError。"""
        known = {f.name: f.type for f in fields(cls)}
        cfg = cls()
        for key, value in data.items():
            if key not in known:
                continue
            default = getattr(cfg, key)
            try:
                if isinstance(default, bool):
                    value = _to_bool(value)
                elif isinstance(default, int):
                    value = int(value)
                elif isinstance(default, str):
                    value = str(value)
            except (TypeError, ValueError) as exc:
                raise ConfigError(f"配置项 {key} 的值 {value!r} 类型错误") from exc
            setattr(cfg, key, value)
        return cfg

    # ------------------------------------------------------------ 读写

    @classmethod
    def load(cls, path: Path | None = None) -> "AppConfig":
        """加载 config.json；文件不存在时返回默认配置。"""
        path = path or paths.config_file()
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"配置文件损坏: {path}") from exc
        if not isinstance(data, dict):
            raise ConfigError(f"配置文件格式错误: {path}")
        return cls.from_dict(data)

    def save(self, path: Path | None = None) -> None:
        path = path or paths.config_file()
        path.write_text(
            json.dumps(self.to_dict(), indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    def update(self, **changes: Any) -> None:
        """就地更新若干字段（带类型转换）。"""
        merged = self.to_dict()
        merged.update(changes)
        new = AppConfig.from_dict(merged)
        for f in fields(self):
            setattr(self, f.name, getattr(new, f.name))


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "on"):
            return True
        if lowered in ("false", "0", "no", "off"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    raise ValueError(f"无法转换为布尔值: {value!r}")


# ------------------------------------------------------------- 进程级单例

_current: AppConfig | None = None


def get_config(reload: bool = False) -> AppConfig:
    """获取进程级配置单例（显式加载，替代旧版模块导入副作用）。"""
    global _current
    if _current is None or reload:
        _current = AppConfig.load()
    return _current


def set_config(cfg: AppConfig) -> None:
    global _current
    _current = cfg
