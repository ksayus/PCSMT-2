"""程序信息 / 设置 API（旧版 ``bin/api/api_program.py`` 的修复版）。

蓝图 ``url_prefix='/api/program'``。修复的旧版 bug：
- CPU/RAM 接口异常路径裸 ``return``（None → 500）→ 现在统一 JSON 错误；
- RAM 接口 ``percent=0`` 时 ``abs_total`` 除零 → 现在直接使用总内存；
- ``/set/settings`` 逐键调 8 个 Change 函数 → 现在 ``update_config`` 一次更新。
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.exceptions import DownloadError
from omniark.interfaces.web.auth import superuser_required
from omniark.services import minecraft_versions, program_service

logger = get_logger()

program_api_bp = Blueprint("program_api", __name__, url_prefix="/api/program")

# 前端字段名 → AppConfig 字段名
_SETTINGS_KEY_MAP = {
    "min_memory": "RunningMemories_Min",
    "max_memory": "RunningMemories_Max",
    "nogui_enabled": "Nogui",
    "eula_wait_time": "WaitEulaGenerateTime",
    "auto_start": "AutomaticStartup",
    "update_source": "AutoUpdateSource",
    "test_versions": "MinecraftTestVersion",
    "storage_update_time": "StorageSizeUpdateTime",
    "server_port": "Port",
}


@program_api_bp.route("/")
def api_index() -> str:
    return "<h1>Welcome to PCSMT2 Program API!</h1>"


@program_api_bp.route("/version")
def version() -> ResponseReturnValue:
    cfg = get_config()
    return jsonify({"version": f"{cfg.PCSMT2_Version}-{cfg.ReleaseVersion}"})


@program_api_bp.route("/minecraft_version")
def minecraft_version() -> ResponseReturnValue:
    """Minecraft 版本列表（网络请求失败返回 502 JSON）。"""
    try:
        versions = minecraft_versions.fetch_minecraft_versions()
    except DownloadError as exc:
        logger.error("获取 Minecraft 版本列表失败: %s", exc)
        return jsonify({"success": False,
                        "error": "获取 Minecraft 版本列表失败"}), 502
    return jsonify({"minecraft_version": versions})


@program_api_bp.route("/disk_usage")
def disk_usage() -> ResponseReturnValue:
    """磁盘占用（字段规范化，替代旧版 disk_usage/disk_free/usage/free 混乱命名）。"""
    return jsonify(program_service.disk_usage())


@program_api_bp.route("/get/settings")
def get_settings() -> ResponseReturnValue:
    cfg = get_config()
    return jsonify({front: getattr(cfg, back)
                    for front, back in _SETTINGS_KEY_MAP.items()})


@program_api_bp.route("/set/settings", methods=["POST"])
@superuser_required
def set_settings() -> ResponseReturnValue:
    """更新程序设置（一次性 update_config，替代旧版 8 个 Change 函数）。"""
    data: dict[str, Any] = request.get_json(silent=True) or {}
    changes = {back: data[front]
               for front, back in _SETTINGS_KEY_MAP.items() if front in data}
    if not changes:
        return jsonify({"success": False,
                        "error": "请求体为空或不包含任何设置项"}), 400
    program_service.update_config(**changes)
    return jsonify({"success": True})


@program_api_bp.route("/get/CPU/Usage")
def cpu_usage() -> ResponseReturnValue:
    """CPU 占用（字段规范化：percent/freq_current/freq_max）。"""
    return jsonify(program_service.cpu_usage())


@program_api_bp.route("/get/RAM/Usage")
def ram_usage() -> ResponseReturnValue:
    """内存占用（字段规范化：percent/used_mb/total_mb）。"""
    return jsonify(program_service.ram_usage())
