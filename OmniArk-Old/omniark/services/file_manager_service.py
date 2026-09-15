"""服务器文件管理服务（替代旧版 Manager.py，供 Web 文件管理器使用）。

旧版 Manager.py 的方法全部无异常处理、成功恒返回 True；
这里统一抛 :class:`FileManagerError`，并强制所有操作限制在
服务器目录之内（修复旧版 Web 端任意目录可读的安全问题）。
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

from omniark.exceptions import OmniArkError
from omniark.services import registry

from pathlib import Path as _Path  # noqa: F401


class FileManagerError(OmniArkError):
    """文件管理操作失败。"""


def _resolve_safe(server_name: str, rel_path: str,
                  root=None) -> tuple[Path, Path]:
    """把相对路径解析为服务器目录内的绝对路径，阻止目录穿越。"""
    server = registry.load_server(server_name, root)
    base = Path(server.Path).resolve()
    target = (base / rel_path.lstrip("/\\")).resolve()
    if base != target and base not in target.parents:
        raise FileManagerError(f"路径越出服务器目录: {rel_path}")
    return base, target


def list_directory(server_name: str, rel_path: str = "",
                   root=None) -> dict:
    """列出目录内容（第一层）。"""
    base, target = _resolve_safe(server_name, rel_path, root)
    if not target.is_dir():
        raise FileManagerError(f"目录不存在: {rel_path}")
    entries = []
    for p in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name)):
        stat = p.stat()
        entries.append({
            "name": p.name,
            "is_dir": p.is_dir(),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime)
            .strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {
        "path": str(target.relative_to(base)) if target != base else "",
        "entries": entries,
    }


def file_status(server_name: str, rel_path: str, root=None) -> dict:
    _, target = _resolve_safe(server_name, rel_path, root)
    if not target.exists():
        raise FileManagerError(f"路径不存在: {rel_path}")
    stat = target.stat()
    return {
        "size": stat.st_size,
        "mod_time": datetime.fromtimestamp(stat.st_mtime)
        .strftime("%Y-%m-%d %H:%M:%S"),
    }


def create_file(server_name: str, rel_path: str, root=None) -> None:
    """创建空文件（不截断已有文件，修复旧版 'w' 截断 bug）。"""
    _, target = _resolve_safe(server_name, rel_path, root)
    if target.exists():
        raise FileManagerError(f"文件已存在: {rel_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.touch()


def create_folder(server_name: str, rel_path: str, root=None) -> None:
    _, target = _resolve_safe(server_name, rel_path, root)
    if target.exists():
        raise FileManagerError(f"目录已存在: {rel_path}")
    target.mkdir(parents=True)


def delete_file(server_name: str, rel_path: str, root=None) -> None:
    _, target = _resolve_safe(server_name, rel_path, root)
    if not target.is_file():
        raise FileManagerError(f"文件不存在: {rel_path}")
    target.unlink()


def delete_folder(server_name: str, rel_path: str, root=None) -> None:
    _, target = _resolve_safe(server_name, rel_path, root)
    if not target.is_dir():
        raise FileManagerError(f"目录不存在: {rel_path}")
    shutil.rmtree(target)


def rename(server_name: str, rel_path: str, new_name: str, root=None) -> None:
    _, target = _resolve_safe(server_name, rel_path, root)
    if not target.exists():
        raise FileManagerError(f"路径不存在: {rel_path}")
    # 新名字不允许带路径分隔符，防穿越
    if "/" in new_name or "\\" in new_name:
        raise FileManagerError("新名称不能包含路径分隔符")
    target.rename(target.with_name(new_name))


def copy(server_name: str, src_rel: str, dst_rel: str, root=None) -> None:
    """复制文件/目录到服务器内另一位置。"""
    _, src = _resolve_safe(server_name, src_rel, root)
    _, dst = _resolve_safe(server_name, dst_rel, root)
    if not src.exists():
        raise FileManagerError(f"源路径不存在: {src_rel}")
    if src.is_dir():
        if dst.exists():
            raise FileManagerError(f"目标已存在: {dst_rel}")
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)


def move(server_name: str, src_rel: str, dst_rel: str, root=None) -> None:
    _, src = _resolve_safe(server_name, src_rel, root)
    _, dst = _resolve_safe(server_name, dst_rel, root)
    if not src.exists():
        raise FileManagerError(f"源路径不存在: {src_rel}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def search(server_name: str, keyword: str, root=None) -> list[str]:
    """在服务器目录内按文件名子串搜索，返回相对路径列表。"""
    base, _ = _resolve_safe(server_name, "", root)
    keyword = keyword.lower()
    results = []
    for p in base.rglob("*"):
        if keyword in p.name.lower():
            results.append(str(p.relative_to(base)))
    return sorted(results)
