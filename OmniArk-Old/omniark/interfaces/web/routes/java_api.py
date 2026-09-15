"""Java 管理器 API。

蓝图 ``url_prefix='/api/java'``：
- 列出已配置映射与系统扫描到的 Java 安装（含实测版本）；
- 手动添加 / 移除 java.exe 路径（添加时通过 ``java -version`` 实测版本）；
- 一键重扫描并回填空缺版本槽位；
- 查询指定服务器核心所需的 Java（展示自动纠正的判定结果）。

写操作（add/remove/rescan）需 admin 角色，查询接口登录即可。
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError
from omniark.interfaces.web.auth import admin_required, superuser_required
from omniark.services import java_service, registry

logger = get_logger()

java_api_bp = Blueprint("java_api", __name__, url_prefix="/api/java")


def _installation_info(path: Path) -> dict:
    version = java_service.java_version(path)
    return {
        "path": str(path),
        "version": version or "未知",
        "major": java_service._java_major(version) if version else None,
    }


@java_api_bp.route("/list")
@admin_required
def java_list() -> ResponseReturnValue:
    """Java 全景：配置映射 + 系统扫描到的安装。"""
    mapping = java_service.load_java_versions()
    configured = [
        {"key": key, "path": path, "valid": bool(path) and Path(path).is_file()}
        for key, path in sorted(mapping.items())
    ]
    installations = [_installation_info(p)
                     for p in java_service.find_java_installations()]
    return jsonify({
        "configured": configured,
        "installations": installations,
        "auto_install_supported": sorted(java_service.CORRETTO_URLS.keys()),
    })


@java_api_bp.route("/add", methods=["POST"])
@superuser_required
def java_add() -> ResponseReturnValue:
    """添加一个 java.exe 路径（实测版本后写入对应版本槽位）。"""
    data = request.get_json(silent=True) or {}
    java_path = str(data.get("path", "")).strip()
    if not java_path:
        return jsonify({"success": False, "error": "path 不能为空"}), 400
    path = Path(java_path)
    if not path.is_file():
        return jsonify({"success": False, "error": "文件不存在"}), 400
    version = java_service.java_version(path)
    if version is None:
        return jsonify({"success": False,
                        "error": "无法识别该文件的 Java 版本（java -version 失败）"}), 400
    major = str(java_service._java_major(version))
    if major == "8":
        major = "1.8"  # 与 java_versions.json 的历史键保持一致
    mapping = java_service.load_java_versions()
    mapping[major] = str(path)
    java_service.save_java_versions(mapping)
    logger.info("Java 路径已添加: %s -> %s", major, path)
    return jsonify({"success": True, "major": major, "version": version})


@java_api_bp.route("/remove", methods=["POST"])
@superuser_required
def java_remove() -> ResponseReturnValue:
    """移除配置映射中的路径（按版本键或按路径匹配）。"""
    data = request.get_json(silent=True) or {}
    key = str(data.get("key", "")).strip()
    target_path = str(data.get("path", "")).strip()
    mapping = java_service.load_java_versions()
    removed = False
    for k, v in list(mapping.items()):
        if (key and k == key) or (target_path and v == target_path):
            mapping[k] = ""
            removed = True
    if not removed:
        return jsonify({"success": False, "error": "未找到匹配的配置项"}), 404
    java_service.save_java_versions(mapping)
    return jsonify({"success": True})


@java_api_bp.route("/rescan", methods=["POST"])
@superuser_required
def java_rescan() -> ResponseReturnValue:
    """重新扫描系统 Java 并回填空缺的版本槽位。"""
    mapping = java_service.load_java_versions()
    filled: list[str] = []
    for installation in java_service.find_java_installations():
        version = java_service.java_version(installation)
        if version is None:
            continue
        major = str(java_service._java_major(version))
        if major == "8":
            major = "1.8"
        # 只回填空槽位或失效槽位，不覆盖用户手动配置
        current = mapping.get(major, "")
        if not current or not Path(current).is_file():
            mapping[major] = str(installation)
            filled.append(major)
    java_service.save_java_versions(mapping)
    return jsonify({"success": True, "filled": sorted(set(filled))})


@java_api_bp.route("/check/<server_name>")
@admin_required
def java_check(server_name: str) -> ResponseReturnValue:
    """预览某台服务器核心的 Java 需求与将被选用的 java（自动纠正结果）。"""
    try:
        server = registry.repair_server_info(server_name)
        core = Path(server.Path) / Path(server.Core).name
        required, source = java_service.required_java_for_server(
            core, server.Version)
        result: dict = {"required": required, "source": source}
        try:
            java_path, _ = java_service.resolve_java_for_server(
                core, server.Version)
            result["resolved"] = java_path
        except OmniArkError as exc:
            result["resolved"] = None
            result["error"] = str(exc)
        return jsonify(result)
    except OmniArkError as exc:
        return jsonify({"success": False, "error": str(exc)}), 404
