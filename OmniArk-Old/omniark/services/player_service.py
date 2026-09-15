"""玩家管理：封禁/解封/OP（走 RCON），以及玩家名单读取。

替代旧版 ``Server.Do.Ban/Unban/Set``（四个函数复制粘贴 90% 相同，
这里统一为一条 RCON 命令通道）与 ``Server.Get.BannedPlayers`` 等。
"""

from __future__ import annotations

import json
from pathlib import Path

import requests

from omniark.core import paths
from omniark.core.logger import get_logger
from omniark.services import rcon_service, registry

logger = get_logger()

MOJANG_PROFILE_URL = "https://api.mojang.com/users/profiles/minecraft/{name}"


# ------------------------------------------------------------ 命令通道

def _server_command(server_name: str, command: str,
                    root: Path | None = None) -> str:
    server = registry.load_server(server_name, root)
    response = rcon_service.execute_command(server, command)
    logger.info("[%s] %s -> %s", server_name, command, response)
    return response


def ban_player(server_name: str, player: str, **kw) -> str:
    return _server_command(server_name, f"ban {player}", **kw)


def ban_ip(server_name: str, ip: str, **kw) -> str:
    return _server_command(server_name, f"ban-ip {ip}", **kw)


def unban_player(server_name: str, player: str, **kw) -> str:
    return _server_command(server_name, f"pardon {player}", **kw)


def unban_ip(server_name: str, ip: str, **kw) -> str:
    return _server_command(server_name, f"pardon-ip {ip}", **kw)


def op_player(server_name: str, player: str, **kw) -> str:
    return _server_command(server_name, f"op {player}", **kw)


def deop_player(server_name: str, player: str, **kw) -> str:
    return _server_command(server_name, f"deop {player}", **kw)


# ------------------------------------------------------------ 名单读取

def _read_player_json(server, filename: str) -> list[dict]:
    file = server.directory / filename
    if not file.is_file():
        return []
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        logger.warning("玩家名单文件损坏: %s", file)
        return []


def banned_players(server_name: str, root: Path | None = None) -> list[str]:
    server = registry.load_server(server_name, root)
    return [p.get("name", "") for p in
            _read_player_json(server, paths.Files.BANNED_PLAYERS)
            if p.get("name")]


def banned_ips(server_name: str, root: Path | None = None) -> list[str]:
    server = registry.load_server(server_name, root)
    return [p.get("ip", "") for p in
            _read_player_json(server, paths.Files.BANNED_IPS)
            if p.get("ip")]


def white_list(server_name: str, root: Path | None = None) -> list[str] | None:
    """白名单玩家列表；未启用白名单返回 None。"""
    from omniark.services import properties
    server = registry.load_server(server_name, root)
    enabled = properties.get_value(server.properties_file, "white-list")
    if (enabled or "").lower() != "true":
        return None
    return [p.get("name", "") for p in
            _read_player_json(server, paths.Files.WHITELIST) if p.get("name")]


def history_players(server_name: str, root: Path | None = None) -> list[str]:
    server = registry.load_server(server_name, root)
    return [p.get("name", "") for p in
            _read_player_json(server, paths.Files.USER_CACHE) if p.get("name")]


def current_players(server_name: str, root: Path | None = None) -> list[str]:
    """当前在线玩家（经 RCON /list）；服务器未运行返回空列表。"""
    server = registry.load_server(server_name, root)
    status = rcon_service.online_status(server)
    return status.players if status else []


# ------------------------------------------------------------ UUID 查询

def query_uuid(player_name: str) -> str | None:
    """通过 Mojang API 查询玩家 UUID，不存在返回 None。"""
    try:
        resp = requests.get(MOJANG_PROFILE_URL.format(name=player_name),
                            timeout=10)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json().get("id")
    except (requests.RequestException, ValueError) as exc:
        logger.error("查询玩家 UUID 失败: %s", exc)
        return None
