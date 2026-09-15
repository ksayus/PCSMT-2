"""终端 API（合并旧版 ``bin/api/ServerSocket.py``：名为 Socket 实为 HTTP）。

修复点：
- POST 不再是桩实现，真正通过 RCON 执行命令；
- POST 增加 ``admin_required`` 鉴权（命令执行属高危操作）。
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import rcon_service, registry, server_service

terminal_bp = Blueprint("terminal_api", __name__, url_prefix="/api/server")


@terminal_bp.route("/terminal/<name>", methods=["GET"])
@admin_required
def terminal_logs(name: str) -> ResponseReturnValue:
    """拉取服务器最近 1000 行终端日志（前端轮询该接口刷新终端视图）。"""
    logs = server_service.get_terminal_logs(name, 1000)
    return jsonify({"success": True, "logs": logs.splitlines()})


@terminal_bp.route("/terminal/<name>", methods=["POST"])
@superuser_required
def terminal_command(name: str) -> ResponseReturnValue:
    """通过 RCON 执行命令（替代旧版的桩实现）。"""
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
