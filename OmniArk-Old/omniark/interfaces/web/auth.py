"""管理员鉴权（替代旧版 api_server.py 中的 admin_required 与 /login）。

修复的旧版问题：
- ``admin_required`` 未使用 ``functools.wraps``（包装后函数名全变成 wrapper）；
- ``session['next_url']`` 存而不用 —— 登录后现在会消费并校验同域；
- ``is_safe_url`` 定义了但从未调用 —— 现在用于防开放重定向；
- 新增 ``/logout`` 路由。
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar
from urllib.parse import urljoin, urlparse

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session, url_for)

from omniark.core.logger import get_logger
from omniark.services import security_service

logger = get_logger()

auth_bp = Blueprint("auth", __name__)

F = TypeVar("F", bound=Callable[..., Any])


def is_safe_url(target: str) -> bool:
    """校验跳转目标与本站同域（防开放重定向）。"""
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and test.netloc == ref.netloc


def admin_required(view: F) -> F:
    """管理员鉴权装饰器。

    未登录时：AJAX/API 请求返回 401 JSON（前端据此跳登录页），
    普通请求把当前 URL 存入 ``session['next_url']`` 后重定向到 /login。
    """

    @functools.wraps(view)
    def wrapper(*args: Any, **kwargs: Any):
        if session.get("authenticated"):
            return view(*args, **kwargs)
        if (request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.path.startswith("/api")):
            return jsonify({"success": False, "error": "未授权，请先登录"}), 401
        session["next_url"] = request.url
        return redirect(url_for("auth.login"))

    return wrapper  # type: ignore[return-value]


def superuser_required(view: F) -> F:
    """管理员（admin 角色）鉴权：已登录但非管理员返回 403。

    权限模型：
    - admin：全部功能（账号管理/程序设置/创建删除服务器/文件写操作/备份恢复等）
    - user（普通用户）：查看 + 服务器启停/重启等日常操作
    """

    @functools.wraps(view)
    def wrapper(*args: Any, **kwargs: Any):
        if not session.get("authenticated"):
            if (request.headers.get("X-Requested-With") == "XMLHttpRequest"
                    or request.path.startswith("/api")):
                return jsonify({"success": False,
                                "error": "未授权，请先登录"}), 401
            session["next_url"] = request.url
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            return jsonify({"success": False,
                            "error": "权限不足：该操作需要管理员权限"}), 403
        return view(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """登录页 / 登录处理（任何有效账户均可登录，权限由角色决定）。"""
    if request.method == "POST":
        account = request.form.get("admin_account", "")
        password = request.form.get("admin_password", "")
        if security_service.verify_admin_password(account, password):
            session.permanent = True  # 登录身份保留 7 天（permanent_session_lifetime）
            session["authenticated"] = True
            session["admin_account"] = account
            session["role"] = security_service.get_role(account)
            logger.info("用户 %s 登录成功（%s）", account, session["role"])
            # 消费 next_url，并校验同域防开放重定向
            next_url = session.pop("next_url", None)
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for("pages.index"))
        logger.warning("用户 %s 登录失败", account)
        return render_template("login.html", error="账号或密码错误")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """登出并回到登录页。"""
    session.pop("authenticated", None)
    session.pop("admin_account", None)
    session.pop("role", None)
    return redirect(url_for("auth.login"))
