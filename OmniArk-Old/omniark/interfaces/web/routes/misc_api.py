"""杂项小路由（旧版 ``bin/api/api.py`` 与 ``Resouce.py`` 的合并）。

修复点：``/api/static/ico`` 使用 ``app.static_folder`` 绝对路径，
不再依赖相对路径 ``'static'``（旧版在打包环境下可能失效）。
"""

from __future__ import annotations

from flask import Blueprint, current_app, send_from_directory
from flask.typing import ResponseReturnValue

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/api")
def api_index() -> str:
    return "<h1>Welcome to PCSMT2 API!</h1>"


@misc_bp.route("/api/static/ico")
def static_ico() -> ResponseReturnValue:
    return send_from_directory(current_app.static_folder, "PCSMT2.ico")
