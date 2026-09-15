"""页面路由（服务端渲染模板）。

替代旧版 ``bin/api/PageServer.py``。修复点：
- ``/server/<name>/storage_chart`` 现在会传模板引用的 ``title``；
- ``/server/create`` POST 成功后重定向到首页（避免刷新重复提交），
  并去掉了旧版 ``sleep(40)+sleep(3)`` 的 43 秒同步阻塞：
  ``register_server`` 已直接写好 ``eula.txt``，无需先启动一次服务器；
- ``/manager/<name>`` 服务器不存在时返回 404。
"""

from __future__ import annotations

from pathlib import Path

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from flask.typing import ResponseReturnValue

from omniark import __version__
from omniark.core.logger import get_logger
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import registry, server_service

logger = get_logger()

pages_bp = Blueprint("pages", __name__)

_STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

# 支持的核心类型（与旧版一致）
CORE_TYPES = {"official", "forge", "fabric", "mohist"}


@pages_bp.route("/")
@admin_required
def index() -> str:
    """主控台首页（SPA 外壳）。默认要求登录。

    SPA 的 main.js / main.css **内联进 HTML 响应**（每次请求从磁盘现读），
    整个主界面永远是一份新鲜文档——不存在单独的 JS/CSS 子资源，
    任何客户端缓存都不可能再让界面停在旧版本。
    """
    inline_js = (_STATIC_DIR / "js" / "main.js").read_text(encoding="utf-8")
    inline_css = (_STATIC_DIR / "css" / "main.css").read_text(encoding="utf-8")
    return render_template("index.html", inline_js=inline_js,
                           inline_css=inline_css)


@pages_bp.route("/server/create", methods=["GET", "POST"])
@superuser_required
def create_server_page() -> ResponseReturnValue:
    """创建服务器页面。POST 创建并重定向回首页。"""
    if request.method == "POST":
        return _handle_create()
    return render_template("CreateServer.html")


def _handle_create() -> ResponseReturnValue:
    form = request.form
    name = form.get("serverName", "").strip()
    core_type = form.get("coreType", "")
    version = form.get("coreVersion", "")
    if not name or not version:
        return jsonify({"success": False, "error": "服务器名与核心版本不能为空"}), 400
    if core_type not in CORE_TYPES:
        return jsonify({"success": False,
                        "error": f"不支持的核心类型: {core_type}"}), 400
    try:
        port = int(form.get("port", "25565"))
    except ValueError:
        return jsonify({"success": False, "error": "端口号必须是整数"}), 400
    if not 1024 <= port <= 65535:
        return jsonify({"success": False,
                        "error": "端口号必须在 1024-65535 之间"}), 400

    # 复选框：勾选时表单同时提交 true/false 两个值，以是否包含 true 为准
    pvp = "true" if "true" in form.getlist("pvpEnabled") else "false"
    online_mode = "true" if "true" in form.getlist("onlineMode") else "false"
    game_mode = form.get("gameMode", "survival")

    server = server_service.create_server(name, core_type, version)
    init_props = {
        "server-port": str(port),
        "pvp": pvp,
        "online-mode": online_mode,
        "gamemode": game_mode,
    }
    # 服务器尚未首次启动时 server.properties 不存在，直接生成初始文件
    props_file = server.properties_file
    if not props_file.is_file():
        props_file.write_text(
            "\n".join(f"{key}={value}" for key, value in init_props.items())
            + "\n",
            encoding="utf-8",
        )
    else:
        server_service.change_properties(server.Name, init_props)
    logger.info("服务器 %s 创建完成", server.Name)
    return redirect(url_for("pages.index"))


@pages_bp.route("/server/<name>/storage_chart")
@admin_required
def storage_chart(name: str) -> str:
    """存储占用折线图页面（修复旧版未传 title 的问题）。"""
    registry.load_server(name)  # 不存在则抛 ServerNotFoundError → 404
    return render_template("chart_js.html", server_name=name,
                           title=f"{name}服务器存储情况")


@pages_bp.route("/server/settings/<name>")
@admin_required
def server_settings(name: str) -> str:
    """服务器配置编辑页（表单数据由页面 JS 调 API 回填）。"""
    registry.load_server(name)
    return render_template("ServerSettings.html", server_name=name)


@pages_bp.route("/manager/<name>")
@admin_required
def file_manager(name: str) -> str:
    """文件管理器页面。"""
    server = registry.repair_server_info(name)
    # 模板同时引用 server_info.name（小写）与 server_info.Name / Path
    server_info = {"name": server.Name, "Name": server.Name,
                   "Path": server.Path}
    return render_template("manager.html", server_info=server_info)
