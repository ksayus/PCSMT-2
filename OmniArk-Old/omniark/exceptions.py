"""OmniArk 统一异常体系。

业务层抛出具体异常，接口层（CLI/Web/GUI）负责捕获并转换为用户可读的提示，
杜绝旧版 ``except Exception: return False`` 式的含糊处理。
"""

from __future__ import annotations


class OmniArkError(Exception):
    """所有 OmniArk 异常的基类。"""


# ---------------------------------------------------------------- 配置 / 环境

class ConfigError(OmniArkError):
    """配置文件缺失、损坏或字段类型错误。"""


class JavaNotFoundError(OmniArkError):
    """未找到可用的 Java 运行环境。"""


# ---------------------------------------------------------------- 服务器管理

class ServerError(OmniArkError):
    """服务器相关操作的基类。"""


class ServerNotFoundError(ServerError):
    """指定的服务器不存在。"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        super().__init__(f"服务器不存在: {server_name}")


class ServerAlreadyExistsError(ServerError):
    """同名服务器已存在。"""

    def __init__(self, server_name: str):
        self.server_name = server_name
        super().__init__(f"服务器已存在: {server_name}")


class ServerRunningError(ServerError):
    """服务器正在运行，无法执行该操作。"""


class CoreFileNotFoundError(ServerError):
    """服务器核心文件缺失。"""


# ---------------------------------------------------------------- 下载 / 网络

class DownloadError(OmniArkError):
    """资源下载失败。"""


class VersionNotFoundError(DownloadError):
    """请求的 Minecraft / 核心版本不存在。"""


# ---------------------------------------------------------------- RCON

class RconError(OmniArkError):
    """RCON 连接或命令执行失败。"""


# ---------------------------------------------------------------- 备份

class BackupError(OmniArkError):
    """备份或回档失败。"""


class BackupNotFoundError(BackupError):
    """指定的备份文件不存在。"""
