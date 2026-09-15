"""文件/目录工具（替代旧版 bin/find_files/* 与散落的 os 调用）。"""

from __future__ import annotations

import os
from pathlib import Path


def find_files_with_extension(directory: str | Path, extension: str) -> list[Path]:
    """递归查找指定后缀的文件。

    :param directory: 搜索根目录
    :param extension: 后缀名（如 '.txt'；空字符串匹配所有文件）
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []
    if extension:
        return sorted(p for p in directory.rglob(f"*{extension}") if p.is_file())
    return sorted(p for p in directory.rglob("*") if p.is_file())


def ensure_file(path: str | Path) -> Path:
    """确保文件存在，不存在则创建空文件（含父目录）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    return path


def ensure_dir(path: str | Path) -> Path:
    """确保目录存在，不存在则创建（含父目录）。"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_tree(root: str | Path) -> list[Path]:
    """递归列出目录下所有路径。"""
    root = Path(root)
    return sorted(root.rglob("*")) if root.is_dir() else []


def list_dir(root: str | Path) -> list[str]:
    """列出目录第一层内容名。"""
    root = Path(root)
    return sorted(os.listdir(root)) if root.is_dir() else []


def directory_size(root: str | Path) -> int:
    """计算目录总大小（字节）。"""
    total = 0
    for p in Path(root).rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                continue
    return total
