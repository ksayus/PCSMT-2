"""程序初始化引导（替代旧版 bin/bootstrap.py + Init.py）。

明确的一次性初始化流程，无任何模块导入副作用：

1. 初始化日志与工作目录
2. 加载/修复 config.json
3. 检查 Java 环境（缺失时按需自动安装）
4. 确保 RSA 密钥对存在
5. 首次运行时创建管理员账户（仅交互模式）
6. 配置开机自启
7. 启动存储统计调度器
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from omniark import PROGRAM_NAME
from omniark.core import paths
from omniark.core.config import AppConfig, get_config, set_config
from omniark.core.logger import attach_file_handler, get_logger, setup_logger
from omniark.exceptions import OmniArkError

logger = get_logger()


def init_workspace(root: Path | None = None) -> Path:
    """初始化工作目录与配置。返回工作根目录。"""
    root = root or paths.workspace_root()
    os.chdir(root)  # 与旧版行为一致：以工作根为基准
    setup_logger()
    attach_file_handler(root)  # 文件日志在此挂载，import 阶段零磁盘副作用
    paths.ensure_directories(root)

    # 加载并修复配置（写回缺失键）
    cfg = AppConfig.load(paths.config_file(root))
    cfg.save(paths.config_file(root))
    set_config(cfg)
    logger.info("工作目录: %s", root)
    return root


def init_java(root: Path | None = None,
              auto_install: bool = False) -> dict[str, str]:
    """检查 java_versions.json 中各版本的 java 路径，返回 {版本: 路径}。

    修复旧版 bug：jdk 前缀误匹配、安装成功后存版本号而非路径。
    """
    from omniark.services import java_service

    mapping = java_service.load_java_versions(root)
    changed = False
    for version, current in mapping.items():
        if current and Path(current).is_file():
            logger.debug("Java %s: %s", version, current)
            continue
        matched = java_service.find_matching_java(version)
        if matched:
            mapping[version] = next(iter(matched))
            changed = True
            logger.info("Java %s 已定位: %s", version, mapping[version])
        elif auto_install and sys.platform == "win32":
            try:
                mapping[version] = java_service.install_java_windows(version)
                changed = True
            except OmniArkError as exc:
                logger.error("Java %s 自动安装失败: %s（可稍后手动安装）",
                             version, exc)
        else:
            logger.warning("未找到 Java %s，部分 Minecraft 版本将无法启动",
                           version)
    if changed:
        java_service.save_java_versions(mapping, root)
    return mapping


def init_security() -> None:
    """确保 RSA 密钥对存在。"""
    from omniark.services import security_service
    security_service.ensure_key_pair()


def ensure_admin_account(interactive: bool = True) -> bool:
    """确保存在管理员账户。

    :param interactive: 允许用 input() 交互创建（GUI 模式应传 False）。
    :return: 是否已存在或成功创建。
    """
    from omniark.services import security_service

    if security_service.admin_account_exists():
        return True
    if not interactive:
        logger.warning("尚无管理员账户，Web 登录功能不可用；"
                       "请通过 CLI 运行一次程序以创建账户")
        return False

    import getpass
    print("首次运行，请创建管理员账户（用于 Web 管理界面登录）")
    account = input("管理员账户名: ").strip()
    if not account:
        logger.error("账户名不能为空")
        return False
    password = getpass.getpass("管理员密码: ")  # 修复旧版明文 input 的问题
    password2 = getpass.getpass("确认密码: ")
    if password != password2:
        logger.error("两次密码不一致")
        return False
    if not password:
        logger.error("密码不能为空")
        return False
    try:
        # 首个账户为管理员
        security_service.create_admin_account(account, password, role="admin")
        return True
    except OmniArkError as exc:
        logger.error("创建管理员账户失败: %s", exc)
        return False


def init_autostart() -> None:
    """按配置同步开机自启状态。"""
    from omniark.services import system_service
    cfg = get_config()
    registered = system_service.is_startup_registered(PROGRAM_NAME)
    if cfg.AutomaticStartup and not registered:
        system_service.add_startup(PROGRAM_NAME)
    elif not cfg.AutomaticStartup and registered:
        system_service.remove_startup(PROGRAM_NAME)


def start_storage_scheduler(root: Path | None = None) -> None:
    """为所有已注册服务器启动存储统计线程。"""
    from omniark.services import registry, storage_service
    for name in registry.list_server_names(root):
        try:
            server = registry.load_server(name, root)
            if server.exists():
                storage_service.scheduler.start(server, root)
        except OmniArkError as exc:
            logger.warning("无法为 %s 启动存储统计: %s", name, exc)


def run_bootstrap(interactive: bool = True,
                  auto_install_java: bool = False,
                  root: Path | None = None) -> Path:
    """完整初始化流程（异常不再 sys.exit，而是记录后继续）。"""
    root = init_workspace(root)
    try:
        init_java(root, auto_install=auto_install_java)
    except OmniArkError as exc:
        logger.error("Java 环境初始化失败: %s", exc)
    try:
        init_security()
        ensure_admin_account(interactive=interactive)
    except OmniArkError as exc:
        logger.error("安全模块初始化失败: %s", exc)
    try:
        init_autostart()
    except OmniArkError as exc:
        logger.error("开机自启配置失败: %s", exc)
    start_storage_scheduler(root)
    logger.info("%s 初始化完成", PROGRAM_NAME)
    return root
