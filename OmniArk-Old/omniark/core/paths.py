"""路径常量与目录管理（统一使用 pathlib，替代旧版字符串拼接）。

旧版 ``bin/export/Info.py`` 中 ``File.Folder`` / ``File.Document`` 的
现代化等价物。所有路径集中在此定义，业务层不再手写 ``'\\saves'`` 之类的
硬编码字符串。

工作根目录默认取当前工作目录（与旧版行为一致，保证数据兼容），
可通过环境变量 ``OMNIARK_HOME`` 覆盖，便于测试与便携部署。
"""

from __future__ import annotations

import os
from pathlib import Path


def workspace_root() -> Path:
    """返回工作根目录（数据目录所在的根）。

    优先级：环境变量 ``OMNIARK_HOME`` > 当前工作目录。
    """
    env = os.environ.get("OMNIARK_HOME")
    if env:
        return Path(env).resolve()
    return Path.cwd()


class _Dirs:
    """相对工作根目录的目录名（与旧版 Info.File.Folder 对应）。"""

    SAVES = "saves"
    SERVER_STORAGE_SIZE = "server_storage_size"
    LOGS = "logs"
    SERVERS = "servers"
    RESOURCE = "resource"
    CORE_INSTALLATION = "resource/core_installation"
    EXCEL = "resource/excel"
    MODS = "mods"        # 服务器实例内部目录
    PLUGINS = "plugins"  # 服务器实例内部目录


class _Files:
    """常用文件名（与旧版 Info.File.Document 对应）。"""

    START_BATCH = "start.bat"
    EULA = "eula.txt"
    SERVER_PROPERTIES = "server.properties"
    CONFIG = "config.json"
    DELETE_OLD_PROGRAM = "delete_old_program.bat"
    LATEST_TXT = "latest.txt"
    LATEST_JSON = "latest.json"
    LATEST_LOG = "latest.log"
    BANNED_PLAYERS = "banned-players.json"
    BANNED_IPS = "banned-ips.json"
    OPS = "ops.json"
    WHITELIST = "whitelist.json"
    USER_CACHE = "usercache.json"
    FORGE_RUN_BATCH = "run.bat"
    FORGE_JVM_ARGS = "@user_jvm_args.txt"
    SERVER_INFO_EXCEL = "AllServerInfo.xlsx"


Dirs = _Dirs()
Files = _Files()


# ------------------------------------------------------------- 绝对路径工厂

def saves_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.SAVES


def storage_size_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.SERVER_STORAGE_SIZE


def logs_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.LOGS


def servers_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.SERVERS


def resource_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.RESOURCE


def core_installation_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.CORE_INSTALLATION


def excel_dir(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Dirs.EXCEL


def config_file(root: Path | None = None) -> Path:
    return (root or workspace_root()) / Files.CONFIG


def server_save_file(server_name: str, root: Path | None = None) -> Path:
    """指定服务器的信息 JSON 文件路径（saves/<name>.json）。"""
    return saves_dir(root) / f"{server_name}.json"


def storage_size_file(server_name: str, root: Path | None = None) -> Path:
    return storage_size_dir(root) / f"{server_name}.json"


# 服务器核心默认文件名（与旧版 Core.DefaultName 对应）
CORE_DEFAULT_NAMES = {
    "official": "official-server.jar",
    "forge": "forge-installer.jar",
    "fabric": "fabric-server-launch.jar",
    "mohist": "mohist-server.jar",
}

# 安装器保存位置（与旧版 Core.Position.*_save 对应）
INSTALLER_FILES = {
    "fabric": "fabric-installer.jar",
    "forge": "forge-installer.jar",
}

# 自动更新仓库地址（与旧版 ProjectRepository 对应）
REPOSITORY_API = {
    "github": "https://api.github.com/repos/ksayus/PCSMT-2/releases/latest",
    "gitee": "https://gitee.com/api/v5/repos/ksayus/PCSMT-2/releases/latest",
}

# RCON 默认配置（本地使用）
RCON_DEFAULT_HOST = "127.0.0.1"
RCON_DEFAULT_PASSWORD = "pcsmt2"


def ensure_directories(root: Path | None = None) -> None:
    """创建工作所需的所有目录（幂等）。"""
    root = root or workspace_root()
    for maker in (saves_dir, storage_size_dir, logs_dir, servers_dir,
                  resource_dir, core_installation_dir, excel_dir):
        maker(root).mkdir(parents=True, exist_ok=True)
