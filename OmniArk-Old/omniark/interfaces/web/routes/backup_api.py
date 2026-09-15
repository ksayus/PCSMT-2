"""备份管理 API。

蓝图 ``url_prefix='/api/server'``（与服务器 API 同前缀，路径为
``/<name>/backups...``）：
- 列表任何登录用户可看；
- 创建/恢复/删除均需 admin 角色；
- 恢复前会自动备份当前存档（``omniark_backups/backup_*_pre-restore.zip``）。
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import backup_service, registry

logger = get_logger()

backup_api_bp = Blueprint("backup_api", __name__, url_prefix="/api/server")


@backup_api_bp.route("/<name>/backups")
@admin_required
def backup_list(name: str) -> ResponseReturnValue:
    """统一列出全部来源的备份（native/mod/plugin）。"""
    registry.load_server(name)  # 不存在 → 404
    return jsonify({"backups": backup_service.list_backups(name)})


@backup_api_bp.route("/<name>/backups/create", methods=["POST"])
@superuser_required
def backup_create(name: str) -> ResponseReturnValue:
    """手动创建原生备份（打包世界目录）。"""
    try:
        path = backup_service.create_backup(name)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "file": path.name})


@backup_api_bp.route("/<name>/backups/restore", methods=["POST"])
@superuser_required
def backup_restore(name: str) -> ResponseReturnValue:
    """回档（回档前自动备份当前存档）。

    body: {"file": "备份名.zip"}；缺省用最新备份。
    """
    data = request.get_json(silent=True) or {}
    backup_file = data.get("file") or None
    try:
        used = backup_service.restore_backup(name, backup_file)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "file": used.name,
                    "message": "回档完成，回档前存档已自动备份"})


@backup_api_bp.route("/<name>/backups/delete", methods=["POST"])
@superuser_required
def backup_delete(name: str) -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    backup_file = str(data.get("file", "")).strip()
    if not backup_file:
        return jsonify({"success": False, "error": "file 不能为空"}), 400
    try:
        backup_service.delete_backup(name, backup_file)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True})
