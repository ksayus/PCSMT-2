"""server.properties 读写服务。

替代旧版 ``find_keyword_inline_and_change_argument``（子串匹配 + 整行覆盖，
会毁注释、误伤相似键），改为精确的 ``key=value`` 解析。
"""

from __future__ import annotations

from pathlib import Path


def read_properties(path: str | Path) -> dict[str, str]:
    """读取 properties 文件为字典（忽略注释与空行，保留原样值）。"""
    path = Path(path)
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for line in _read_lines(path):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "!")):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def get_value(path: str | Path, key: str) -> str | None:
    """获取指定键的值，不存在返回 None。"""
    return read_properties(path).get(key)


def set_value(path: str | Path, key: str, value: str) -> bool:
    """精确修改指定键的值（保持其余行原样）。

    键不存在时在文件末尾追加。返回是否成功。
    """
    path = Path(path)
    if not path.is_file():
        return False
    lines = _read_lines(path)
    replaced = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("#", "!")) or "=" not in stripped:
            continue
        line_key = stripped.partition("=")[0].strip()
        if line_key == key:  # 精确匹配，不是子串
            lines[i] = f"{key}={value}\n"
            replaced = True
    if not replaced:
        lines.append(f"{key}={value}\n")
    path.write_text("".join(lines), encoding="utf-8")
    return True


def set_values(path: str | Path, values: dict[str, str]) -> None:
    """批量修改（一次读写，替代旧版一个接口调 14 次 set）。"""
    path = Path(path)
    if not path.is_file():
        return
    lines = _read_lines(path)
    remaining = dict(values)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("#", "!")) or "=" not in stripped:
            continue
        line_key = stripped.partition("=")[0].strip()
        if line_key in remaining:
            lines[i] = f"{line_key}={remaining.pop(line_key)}\n"
    for key, value in remaining.items():
        lines.append(f"{key}={value}\n")
    path.write_text("".join(lines), encoding="utf-8")


def _read_lines(path: Path) -> list[str]:
    """读取文件行（utf-8，失败回退 ISO-8859-1）。"""
    try:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        return path.read_text(encoding="ISO-8859-1").splitlines(keepends=True)
