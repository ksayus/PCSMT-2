"""服务器管理 API（旧版 ``bin/api/api_server.py`` 的修复版）。

蓝图 ``url_prefix='/api/server'``。修复的旧版 bug：
- ``/list`` 的 ``serverCount`` 返回 ``str(列表)`` → 现在返回 ``len``；
- ``/<name>/command`` 装饰器顺序错误导致鉴权失效 → 现在 ``admin_required``
  位于 ``@route`` 之下（正确顺序）；
- ``/latest`` 文件缺失时 ``return False`` → 现在返回 404 JSON；
- ``/get/<name>/terminal/logs`` 成功路径无返回值 → 现在正常返回日志；
- ``/status/<name>`` 用 502 表示"已停止" → 现在一律 200，用 status 字段区分；
- ``/set/settings/<name>`` 逐字段调 14 次修改 → 现在一次性批量设置。
"""

from __future__ import annotations

import json
import re

from flask import Blueprint, jsonify, request, send_file
from flask.typing import ResponseReturnValue

from omniark.core import paths
from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import (player_service, process_manager, properties,
                              rcon_service, registry, server_service,
                              storage_service)

logger = get_logger()

server_api_bp = Blueprint("server_api", __name__, url_prefix="/api/server")

# 解析 "54.89MB" 这类可读大小字符串
_SIZE_RE = re.compile(r"^\s*([\d.]+)\s*(B|KB|MB|GB|TB|PB)\s*$")

# /set/settings 表单中的 properties 文本字段与复选框字段
_PROPERTY_TEXT_FIELDS = ("server-port", "gamemode", "difficulty",
                         "max-players", "max-world-size", "spawn-protection")
_PROPERTY_CHECKBOXES = ("spawn-monsters", "pvp", "allow-flight",
                        "enable-command-block", "white-list",
                        "online-mode", "hardcore")


@server_api_bp.route("/")
def api_index() -> str:
    return "<h1>Welcome to PCSMT2 Server API!</h1>"


# ------------------------------------------------------------ 列表 / 信息

@server_api_bp.route("/list")
def server_list() -> ResponseReturnValue:
    """服务器名列表。修复旧版 serverCount 返回 str(列表) 的 bug。"""
    names = registry.list_server_names()
    return jsonify({"serverlist": names, "serverCount": len(names)})


@server_api_bp.route("/players/<name>")
def server_players(name: str) -> ResponseReturnValue:
    """当前在线玩家：[在线数, 上限, [玩家名...]]；未运行时 players 为 null。"""
    server = registry.load_server(name)
    status = rcon_service.online_status(server)
    if status is None:
        return jsonify({"server": name, "players": None})
    players = player_service.current_players(name)
    return jsonify({"server": name,
                    "players": [status.online, status.maximum, players]})


@server_api_bp.route("/info/<name>")
def server_info(name: str) -> ResponseReturnValue:
    server = registry.repair_server_info(name)
    return jsonify({
        "version": server.Version,
        "size": server.Size,
        "startCount": server.Counts,
        "LatestStartedTime": server.LatestStartedTime,
    })


@server_api_bp.route("/latest")
def latest_server() -> ResponseReturnValue:
    """最近启动的服务器信息（读 resource/latest.json）。"""
    latest_json = paths.resource_dir() / paths.Files.LATEST_JSON
    if not latest_json.is_file():
        # 修复旧版 return False 的非法响应
        return jsonify({"success": False,
                        "error": "暂无最近启动的服务器记录"}), 404
    try:
        data = json.loads(latest_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return jsonify({"success": False,
                        "error": "最近启动记录文件已损坏"}), 500
    return jsonify({
        "name": data.get("Name", ""),
        "version": data.get("Version", ""),
        "size": data.get("Size", ""),
        "startCount": data.get("Counts", 0),
        "LatestStartedTime": data.get("LatestStartedTime") or "N/A",
    })


@server_api_bp.route("/status/<name>")
def server_status(name: str) -> ResponseReturnValue:
    """服务器运行状态（进程 PID 存活或 RCON 可连均视为运行中）。

    一律 200：运行 {"status":"running"}，未运行 {"status":"stopped"}
    （修复旧版用 502 表示停止的语义滥用）。
    """
    server = registry.load_server(name)
    running = process_manager.is_running(server.Name, server.Path) \
        or rcon_service.server_running(server)
    if running:
        return jsonify({"status": "running", "message": "服务器已启动",
                        "online": True})
    return jsonify({"status": "stopped", "message": "服务器未启动",
                    "online": False})


# ------------------------------------------------------------ 生命周期（需鉴权）

@server_api_bp.route("/<name>/start", methods=["POST"])
@admin_required
def start_server(name: str) -> ResponseReturnValue:
    server_service.start_server(name)
    return jsonify({"status": "starting"})


@server_api_bp.route("/<name>/stop", methods=["POST"])
@admin_required
def stop_server(name: str) -> ResponseReturnValue:
    server_service.stop_server(name)
    return jsonify({"status": "stopped"})


@server_api_bp.route("/<name>/restart", methods=["POST"])
@admin_required
def restart_server(name: str) -> ResponseReturnValue:
    server_service.restart_server(name)
    return jsonify({"status": "restarting"})


@server_api_bp.route("/delete/<name>", methods=["POST"])
@superuser_required
def delete_server(name: str) -> ResponseReturnValue:
    server_service.delete_server(name)
    return jsonify({"status": "deleted"})


# ------------------------------------------------------------ 存储统计 / Excel

@server_api_bp.route("/<name>/storage_info")
def storage_info(name: str) -> ResponseReturnValue:
    """存储占用历史（剥离单位转为 float，供 chart.js 画折线图）。"""
    registry.load_server(name)
    history = storage_service.get_storage_history(name)
    labels: list[str] = []
    values: list[float] = []
    unit = "MB"
    for size_str, time_str in zip(history["storage_size"], history["time"]):
        match = _SIZE_RE.match(str(size_str))
        if not match:
            logger.warning("无法解析存储大小记录: %s", size_str)
            continue
        values.append(float(match.group(1)))
        labels.append(time_str)
        unit = match.group(2)
    if not values:
        return jsonify({"success": False, "error": "未找到信息"}), 400
    return jsonify({
        "title": f"{name}服务器存储情况",
        "labels": labels,
        "values": values,
        "type": unit,
    })


@server_api_bp.route("/info/<name>/excel", methods=["POST"])
def server_info_excel(name: str) -> ResponseReturnValue:
    """导出单个服务器信息 Excel（附件下载）。"""
    server = registry.repair_server_info(name)
    extra = {
        "history_players": player_service.history_players(name),
        "white_list": player_service.white_list(name) or [],
        "banned_players": player_service.banned_players(name),
        "current_players": player_service.current_players(name),
    }
    file_path = storage_service.export_server_excel(server, extra)
    return send_file(file_path, as_attachment=True)


@server_api_bp.route("/list/excel", methods=["POST"])
def server_list_excel() -> ResponseReturnValue:
    """导出全部服务器信息 Excel（多 sheet，附件下载）。"""
    servers = []
    for server_name in registry.list_server_names():
        try:
            servers.append(registry.repair_server_info(server_name))
        except OmniArkError as exc:
            logger.warning("跳过无法加载的服务器 %s: %s", server_name, exc)
    file_path = storage_service.export_all_servers_excel(servers)
    return send_file(file_path, as_attachment=True)


# ------------------------------------------------------------ 配置读写

@server_api_bp.route("/get/document/server.properties/<name>")
def get_server_properties(name: str) -> ResponseReturnValue:
    """读取 server.properties 为 JSON 对象。"""
    server = registry.load_server(name)
    return jsonify(properties.read_properties(server.properties_file))


@server_api_bp.route("/get/run_memory/<name>")
def get_run_memory(name: str) -> ResponseReturnValue:
    """读取启动脚本中的 Xms/Xmx。"""
    memory = server_service.get_run_memory(name)
    return jsonify({"min": memory["Xms"], "max": memory["Xmx"]})


@server_api_bp.route("/set/settings/<name>", methods=["POST"])
@superuser_required
def set_server_settings(name: str) -> ResponseReturnValue:
    """批量修改服务器设置（一次性收集表单字段，替代旧版逐字段调 14 次）。"""
    registry.load_server(name)  # 提前校验存在性 → 404
    form = request.form

    # 1) server.properties：文本字段 + 复选框一次批量写入
    values: dict[str, str] = {}
    for key in _PROPERTY_TEXT_FIELDS:
        value = form.get(key)
        if value is not None:
            values[key] = value
    for key in _PROPERTY_CHECKBOXES:
        # 未勾选的复选框不会提交，一律显式写 true/false
        values[key] = "true" if form.get(key) == "on" else "false"
    if values:
        server_service.change_properties(name, values)

    # 2) 运行内存
    min_mem, max_mem = form.get("min-memory"), form.get("max-memory")
    if min_mem and max_mem:
        try:
            server_service.change_run_memory(name, int(min_mem), int(max_mem))
        except ValueError:
            return jsonify({"success": False,
                            "error": "内存参数必须是整数"}), 400

    # 3) 重命名
    new_name = (form.get("serverName") or "").strip()
    if new_name and new_name != name:
        server_service.rename_server(name, new_name)

    return jsonify({"success": True, "message": "修改成功"})


# ------------------------------------------------------------ 终端 / 命令

@server_api_bp.route("/get/<name>/terminal/logs")
def get_terminal_logs(name: str) -> ResponseReturnValue:
    """读取终端日志（修复旧版成功路径无返回值的 bug）。"""
    logs = server_service.get_terminal_logs(name)
    return jsonify({"success": True, "logs": logs.splitlines()})


@server_api_bp.route("/<name>/command", methods=["POST"])
@superuser_required  # 命令执行等同服务器控制台权限，仅管理员；且必须位于 @route 之下
def execute_command(name: str) -> ResponseReturnValue:
    """通过 RCON 在服务器上执行命令。"""
    data = request.get_json(silent=True) or {}
    command = (data.get("command") or "").strip()
    if not command:
        return jsonify({"success": False, "error": "缺少 command 参数"}), 400
    server = registry.load_server(name)
    if not rcon_service.server_running(server):
        return jsonify({"success": False, "error": "服务器未启动",
                        "message": "服务器未启动"})
    result = rcon_service.execute_command(server, command)
    return jsonify({"success": True, "message": result})


# ------------------------------------------------------------ 玩家名单

@server_api_bp.route("/get/banned/players/<name>")
def get_banned_players(name: str) -> ResponseReturnValue:
    players = player_service.banned_players(name)
    return jsonify({"success": True, "message": "获取封禁玩家列表成功",
                    "BannedPlayerList": players})


@server_api_bp.route("/get/banned/ips/<name>")
def get_banned_ips(name: str) -> ResponseReturnValue:
    ips = player_service.banned_ips(name)
    return jsonify({"success": True, "message": "获取封禁IP列表成功",
                    "BannedIPList": ips})


@server_api_bp.route("/get/white-list/<name>")
def get_white_list(name: str) -> ResponseReturnValue:
    white = player_service.white_list(name)
    if white is None:
        return jsonify({"success": False, "message": "白名单未启用"})
    return jsonify({"success": True, "message": "获取白名单成功",
                    "WhiteList": white})


@server_api_bp.route("/get/history/players/<name>")
def get_history_players(name: str) -> ResponseReturnValue:
    players = player_service.history_players(name)
    if not players:
        return jsonify({"success": False, "message": "无历史玩家"})
    return jsonify({"success": True, "message": "获取历史玩家成功",
                    "HistoryPlayerList": players})
