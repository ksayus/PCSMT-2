"""文件管理器 API（旧版完全未实现，本模块为新增实现）。

所有操作经 :mod:`omniark.services.file_manager_service`，并强制限制在
服务器目录之内。同时保留旧前端使用的 ``/api/get/directory``（legacy_bp），
但修复了旧版 ``replace('..','')`` 可绕过的任意目录可读漏洞：目标路径
必须位于某个已注册服务器的目录内。

前端 ``manager.js`` 传的是绝对路径，本模块统一先转换为服务器目录内的
相对路径再交给业务层。
"""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any, Callable

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.models.server import ServerInstance
from omniark.services import file_manager_service, registry
from omniark.services.file_manager_service import FileManagerError

logger = get_logger()

manager_bp = Blueprint("manager_api", __name__, url_prefix="/api/manager")
legacy_bp = Blueprint("manager_legacy", __name__)


def _to_relative(server: ServerInstance, raw_path: str) -> str:
    """把前端传来的路径（绝对或相对）统一为服务器目录内的相对路径。

    绝对路径必须位于服务器目录内，否则抛 :class:`FileManagerError`。
    """
    raw_path = (raw_path or "").strip()
    if not raw_path:
        return ""
    base = Path(server.Path).resolve()
    candidate = Path(raw_path)
    if candidate.is_absolute():
        target = candidate.resolve()
        if target != base and base not in target.parents:
            raise FileManagerError(f"路径越出服务器目录: {raw_path}")
        return str(target.relative_to(base))
    return raw_path


def _json_body() -> dict[str, Any]:
    """解析 JSON 请求体（容错：非法 JSON 按空处理）。"""
    return request.get_json(silent=True) or {}


def _require_path(body: dict[str, Any], key: str = "path") -> str:
    value = (body.get(key) or "").strip()
    if not value:
        raise FileManagerError(f"缺少 {key} 参数")
    return value


# ------------------------------------------------------------ 目录浏览

@manager_bp.route("/<server_name>/list")
@admin_required
def list_directory(server_name: str) -> ResponseReturnValue:
    """列出目录内容（同时返回新格式 entries 与旧格式 CurrentDirectory）。"""
    server = registry.load_server(server_name)
    rel = _to_relative(server, request.args.get("path", ""))
    data = file_manager_service.list_directory(server_name, rel)
    entries = data["entries"]
    return jsonify({
        "success": True,
        "path": data["path"],
        "entries": entries,
        # 兼容旧前端字段
        "FilesCounts": len(entries),
        "CurrentDirectory": [entry["name"] for entry in entries],
    })


@legacy_bp.route("/api/get/directory")
@admin_required
def legacy_get_directory() -> ResponseReturnValue:
    """旧版目录浏览接口（限制在已注册服务器目录内，修复任意目录可读漏洞）。"""
    raw = request.args.get("path", "")
    if not raw:
        return jsonify({"success": False, "error": "缺少 path 参数"}), 400
    target = Path(raw).resolve()
    for name in registry.list_server_names():
        try:
            server = registry.load_server(name)
        except OmniArkError:
            continue
        base = Path(server.Path).resolve()
        if target == base or base in target.parents:
            rel = str(target.relative_to(base)) if target != base else ""
            try:
                data = file_manager_service.list_directory(name, rel)
            except FileManagerError as exc:
                return jsonify({"success": False, "error": str(exc)}), 404
            entries = data["entries"]
            return jsonify({
                "FilesCounts": len(entries),
                "CurrentDirectory": [entry["name"] for entry in entries],
            })
    return jsonify({"success": False,
                    "error": "路径不存在或不在任何服务器目录内"}), 404


# ------------------------------------------------------------ 创建 / 删除

@manager_bp.route("/<server_name>/create/file", methods=["POST"])
@superuser_required
def create_file(server_name: str) -> ResponseReturnValue:
    server = registry.load_server(server_name)
    rel = _to_relative(server, _require_path(_json_body()))
    file_manager_service.create_file(server_name, rel)
    return jsonify({"success": True, "message": "文件创建成功"})


@manager_bp.route("/<server_name>/create/folder", methods=["POST"])
@superuser_required
def create_folder(server_name: str) -> ResponseReturnValue:
    server = registry.load_server(server_name)
    rel = _to_relative(server, _require_path(_json_body()))
    file_manager_service.create_folder(server_name, rel)
    return jsonify({"success": True, "message": "文件夹创建成功"})


@manager_bp.route("/<server_name>/delete/file", methods=["POST"])
@superuser_required
def delete_file(server_name: str) -> ResponseReturnValue:
    server = registry.load_server(server_name)
    rel = _to_relative(server, _require_path(_json_body()))
    file_manager_service.delete_file(server_name, rel)
    return jsonify({"success": True, "message": "文件删除成功"})


@manager_bp.route("/<server_name>/delete/folder", methods=["POST"])
@superuser_required
def delete_folder(server_name: str) -> ResponseReturnValue:
    server = registry.load_server(server_name)
    rel = _to_relative(server, _require_path(_json_body()))
    file_manager_service.delete_folder(server_name, rel)
    return jsonify({"success": True, "message": "文件夹删除成功"})


# ------------------------------------------------------------ 重命名 / 复制 / 移动

@manager_bp.route("/<server_name>/rename", methods=["POST"])
@superuser_required
def rename(server_name: str) -> ResponseReturnValue:
    body = _json_body()
    old_raw = _require_path(body, "old_path")
    new_raw = _require_path(body, "new_path")
    server = registry.load_server(server_name)
    old_rel = _to_relative(server, old_raw)
    # 前端传的是完整新路径，重命名只取文件名部分（所在目录不变）
    new_name = PurePath(new_raw.replace("\\", "/")).name
    file_manager_service.rename(server_name, old_rel, new_name)
    return jsonify({"success": True, "message": "重命名成功"})


@manager_bp.route("/<server_name>/copy", methods=["POST"])
@superuser_required
def copy(server_name: str) -> ResponseReturnValue:
    return _transfer(server_name, file_manager_service.copy, "复制")


@manager_bp.route("/<server_name>/move", methods=["POST"])
@superuser_required
def move(server_name: str) -> ResponseReturnValue:
    return _transfer(server_name, file_manager_service.move, "移动")


def _transfer(server_name: str,
              operation: Callable[[str, str, str], None],
              verb: str) -> ResponseReturnValue:
    """批量复制/移动：把 source_paths 中各项放入 target_path 目录。"""
    body = _json_body()
    sources: list[str] = body.get("source_paths") or []
    target_raw = (body.get("target_path") or "").strip()
    if not sources or not target_raw:
        return jsonify({"success": False,
                        "error": "缺少 source_paths 或 target_path 参数"}), 400
    server = registry.load_server(server_name)
    target_rel = _to_relative(server, target_raw)

    done = 0
    errors: list[str] = []
    for raw in sources:
        src_rel = _to_relative(server, raw)
        item_name = PurePath(src_rel.replace("\\", "/")).name
        dst_rel = f"{target_rel}/{item_name}" if target_rel else item_name
        try:
            operation(server_name, src_rel, dst_rel)
            done += 1
        except FileManagerError as exc:
            errors.append(str(exc))
    if errors:
        return jsonify({
            "success": False,
            "error": f"{verb}完成 {done} 个，失败 {len(errors)} 个: "
                     + "; ".join(errors),
        }), 400
    return jsonify({"success": True, "message": f"已{verb} {done} 个项目"})
