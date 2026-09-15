"""账号管理 API（多账号 + 权限级别：创建/删除/列表/改密/改权限）。

蓝图 ``url_prefix='/api/account'``：
- ``/me`` 任何登录用户可查自己的身份与权限级别；
- 其余管理操作均需 admin 角色（``superuser_required``）；
- 新建账户默认普通用户；Ksayus 恒为超级管理员（不可删除/降级）。

数据仍存放在 ``C:\\PCSMT2-key\\account\\``（新版 JSON 内含角色字段，
旧版裸密文格式自动兼容为 admin）。
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from flask.typing import ResponseReturnValue

from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import security_service

logger = get_logger()

account_api_bp = Blueprint("account_api", __name__, url_prefix="/api/account")


@account_api_bp.route("/me")
@admin_required
def account_me() -> ResponseReturnValue:
    """当前登录用户身份与权限级别（前端据此做权限感知 UI）。"""
    account = session.get("admin_account", "")
    return jsonify({
        "account": account,
        "role": session.get("role", security_service.DEFAULT_ROLE),
        "super_admin": account.lower() == security_service.SUPER_ADMIN.lower(),
    })


@account_api_bp.route("/list")
@superuser_required
def account_list() -> ResponseReturnValue:
    return jsonify({
        "accounts": security_service.list_accounts_with_roles(),
        "super_admin": security_service.SUPER_ADMIN,
    })


@account_api_bp.route("/create", methods=["POST"])
@superuser_required
def account_create() -> ResponseReturnValue:
    """创建账户（默认普通用户，可显式指定 role）。"""
    data = request.get_json(silent=True) or {}
    account = str(data.get("account", "")).strip()
    password = str(data.get("password", ""))
    role = str(data.get("role", security_service.DEFAULT_ROLE))
    if not account or not password:
        return jsonify({"success": False,
                        "error": "账户名与密码不能为空"}), 400
    try:
        security_service.create_admin_account(account, password, role=role)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True,
                    "role": security_service.get_role(account)})


@account_api_bp.route("/delete", methods=["POST"])
@superuser_required
def account_delete() -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    account = str(data.get("account", "")).strip()
    try:
        security_service.delete_admin_account(account)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True})


@account_api_bp.route("/password", methods=["POST"])
@admin_required
def account_password() -> ResponseReturnValue:
    """改密：普通用户只能改自己；管理员可改任何人（仍需旧密码）。"""
    data = request.get_json(silent=True) or {}
    account = str(data.get("account", "")).strip()
    if session.get("role") != "admin" \
            and account != session.get("admin_account"):
        return jsonify({"success": False,
                        "error": "权限不足：只能修改自己的密码"}), 403
    try:
        security_service.change_admin_password(
            account, str(data.get("old_password", "")),
            str(data.get("new_password", "")))
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True})


@account_api_bp.route("/role", methods=["POST"])
@superuser_required
def account_role() -> ResponseReturnValue:
    """修改账户权限级别（Ksayus 不可降级）。"""
    data = request.get_json(silent=True) or {}
    account = str(data.get("account", "")).strip()
    role = str(data.get("role", ""))
    try:
        security_service.set_role(account, role)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    return jsonify({"success": True, "role": security_service.get_role(account)})
