"""RCON 远程控制服务（替代旧版 bin/export/RCON.py）。

修复的旧版 bug：
- Get.RCON_Object 返回已断开的连接对象
- 端口推导无结果时 UnboundLocalError 被静默吞掉
- EnableRCON 返回字符串而非 bool
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mcrcon import MCRcon

from omniark.core import paths as path_consts
from omniark.core.logger import get_logger
from omniark.exceptions import RconError
from omniark.models.server import ServerInstance
from omniark.services import properties

logger = get_logger()

DEFAULT_PORT_MIN, DEFAULT_PORT_MAX = 0, 65535


@dataclass
class OnlineStatus:
    """服务器在线状态。"""
    online: int = 0
    maximum: int = 0
    players: list[str] = field(default_factory=list)


def setup_rcon(server: ServerInstance,
               password: str = path_consts.RCON_DEFAULT_PASSWORD) -> int:
    """为服务器配置并启用 RCON，返回 rcon 端口。

    端口推导：server-port + 10（越界则 -10，仍越界抛 RconError）。
    """
    props_file = server.properties_file
    server_port_str = properties.get_value(props_file, "server-port")
    try:
        server_port = int(server_port_str) if server_port_str else 25565
    except ValueError:
        server_port = 25565

    rcon_port = server_port + 10
    if not 1 <= rcon_port <= 65535:
        rcon_port = server_port - 10
    if not 1 <= rcon_port <= 65535:
        raise RconError(f"无法为 {server.Name} 推导可用的 RCON 端口")

    properties.set_values(props_file, {
        "enable-rcon": "true",
        "rcon.port": str(rcon_port),
        "rcon.password": password,
    })
    logger.info("服务器 %s 的 RCON 已配置，端口 %d", server.Name, rcon_port)
    return rcon_port


def get_rcon_port(server: ServerInstance) -> int | None:
    """从 server.properties 读取 rcon.port。"""
    value = properties.get_value(server.properties_file, "rcon.port")
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def is_rcon_enabled(server: ServerInstance) -> bool:
    value = properties.get_value(server.properties_file, "enable-rcon")
    return (value or "").lower() == "true"


def execute_command(server: ServerInstance, command: str,
                    host: str = path_consts.RCON_DEFAULT_HOST,
                    password: str = path_consts.RCON_DEFAULT_PASSWORD,
                    timeout: float = 10.0) -> str:
    """通过 RCON 执行命令并返回响应。失败抛 RconError。"""
    port = get_rcon_port(server)
    if port is None:
        raise RconError(f"服务器 {server.Name} 未配置 RCON 端口")
    command = command.lstrip("/")
    try:
        with MCRcon(host, password, port=port, timeout=timeout) as mcr:
            response = mcr.command(command)
    except Exception as exc:  # mcrcon 抛出的异常类型不统一，在此收敛
        raise RconError(f"RCON 命令执行失败: {exc}") from exc
    logger.debug("RCON [%s] %s -> %s", server.Name, command, response)
    return response


def server_running(server: ServerInstance) -> bool:
    """通过能否建立 RCON 连接判断服务器是否在运行。"""
    if get_rcon_port(server) is None:
        return False
    try:
        execute_command(server, "list", timeout=3.0)
        return True
    except RconError:
        return False


def online_status(server: ServerInstance) -> OnlineStatus | None:
    """获取在线玩家信息（解析原版 /list 输出）；未运行返回 None。

    解析 'There are X of a max of Y players online: a, b' 格式，
    兼容部分核心的变体格式。
    """
    try:
        response = execute_command(server, "list", timeout=5.0)
    except RconError:
        return None
    status = OnlineStatus()
    # 例: "There are 2 of a max of 20 players online: Steve, Alex"
    import re
    match = re.search(r"There are (\d+) of a max of (\d+) players online:?\s*(.*)",
                      response)
    if match:
        status.online = int(match.group(1))
        status.maximum = int(match.group(2))
        players_str = match.group(3).strip()
        if players_str:
            status.players = [p.strip() for p in players_str.split(",") if p.strip()]
        return status
    # 兼容 "There are X/Y players online" 变体
    match = re.search(r"There are (\d+)/(\d+) players online:?\s*(.*)", response)
    if match:
        status.online = int(match.group(1))
        status.maximum = int(match.group(2))
        players_str = match.group(3).strip()
        if players_str:
            status.players = [p.strip() for p in players_str.split(",") if p.strip()]
        return status
    logger.warning("无法解析 /list 输出: %s", response)
    return None
