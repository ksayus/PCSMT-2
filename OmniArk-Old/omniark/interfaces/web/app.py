"""Flask 应用工厂（蓝图架构）。

替代旧版 ``bin/api/main.py`` 的单例注册模式：
- 路由按职责拆分为蓝图（pages / server_api / program_api / manager_api /
  terminal_api / misc），在 :func:`create_app` 中统一注册；
- ``template_folder`` / ``static_folder`` 基于 ``Path(__file__).parent``，
  不再依赖 ``os.getcwd()``；
- ``secret_key`` 从工作目录 ``.secret_key`` 文件读取，不存在则随机生成写入，
  修复旧版硬编码 ``'pcsmt2'`` 的安全弱点；
- 统一注册 :class:`OmniArkError` 的 errorhandler，错误响应格式一致。
"""

from __future__ import annotations

import secrets
import time
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from omniark import __version__
from omniark.core import paths
from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError, ServerNotFoundError

logger = get_logger()

_WEB_DIR = Path(__file__).resolve().parent
SECRET_KEY_FILENAME = ".secret_key"


def _load_or_create_secret_key() -> str:
    """从工作目录 ``.secret_key`` 读取密钥；不存在则随机生成并写入。"""
    key_file = paths.workspace_root() / SECRET_KEY_FILENAME
    if key_file.is_file():
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            return key
    key = secrets.token_hex(32)
    try:
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(key, encoding="utf-8")
        logger.info("已生成新的 secret_key: %s", key_file)
    except OSError as exc:
        # 工作目录不可写时使用内存密钥（进程内一致即可）
        logger.warning("secret_key 无法写入磁盘（%s），本次会话使用临时密钥", exc)
    return key


def create_app() -> Flask:
    """应用工厂：创建并配置 Flask 应用，注册全部蓝图与错误处理器。"""
    app = Flask(
        __name__,
        template_folder=str(_WEB_DIR / "templates"),
        static_folder=str(_WEB_DIR / "static"),
    )
    app.secret_key = _load_or_create_secret_key()
    # 登录身份保留：会话 Cookie 7 天有效
    app.permanent_session_lifetime = timedelta(days=7)
    # 静态资源缓存击穿：版本号 + 本次进程启动时间戳。
    # 每次启动程序 URL 都不同，WebView2/浏览器缓存永远不可能命中旧文件
    # （本地应用无 CDN，牺牲缓存换"更新必生效"）。
    app.config["ASSET_VERSION"] = f"{__version__}.{int(time.time())}"
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    paths.ensure_directories()

    @app.after_request
    def _no_cache_dynamic(resp):
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" in content_type or "javascript" in content_type \
                or "text/css" in content_type:
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
        return resp

    @app.context_processor
    def _inject_asset_version():
        """所有模板可引用 {{ asset_version }} 做静态资源缓存击穿。"""
        return {"asset_version": app.config["ASSET_VERSION"]}

    # 延迟导入蓝图，避免模块级循环依赖
    from omniark.interfaces.web.auth import auth_bp
    from omniark.interfaces.web.routes import (
        account_api, backup_api, java_api, manager_api, misc_api, pages,
        program_api, server_api, terminal_api,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages.pages_bp)
    app.register_blueprint(server_api.server_api_bp)
    app.register_blueprint(program_api.program_api_bp)
    app.register_blueprint(manager_api.manager_bp)
    app.register_blueprint(manager_api.legacy_bp)
    app.register_blueprint(terminal_api.terminal_bp)
    app.register_blueprint(misc_api.misc_bp)
    app.register_blueprint(java_api.java_api_bp)
    app.register_blueprint(account_api.account_api_bp)
    app.register_blueprint(backup_api.backup_api_bp)

    _register_error_handlers(app)
    return app


def _register_error_handlers(app: Flask) -> None:
    """统一错误处理：OmniArkError → 400/404，未预期异常 → 500 JSON。"""

    @app.errorhandler(OmniArkError)
    def handle_omniark_error(exc: OmniArkError):
        # ServerNotFoundError → 404，其余业务异常 → 400
        status = 404 if isinstance(exc, ServerNotFoundError) else 400
        logger.warning("业务错误: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), status

    @app.errorhandler(404)
    def handle_not_found(exc: HTTPException):
        if request.path.startswith("/api"):
            return jsonify({"success": False, "error": "接口不存在"}), 404
        return "<h1>404 Not Found</h1>", 404

    @app.errorhandler(Exception)
    def handle_internal_error(exc: Exception):
        # HTTPException（如 405）交还给默认处理
        if isinstance(exc, HTTPException):
            return exc
        logger.exception("未处理的内部错误")
        return jsonify({"success": False, "error": "服务器内部错误"}), 500


def run(host: str = "127.0.0.1", port: int | None = None) -> None:
    """启动开发服务器；port 为 None 时读取配置 ``get_config().Port``。"""
    app = create_app()
    app.run(host=host, port=port or get_config().Port)
