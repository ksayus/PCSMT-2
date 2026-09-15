"""Java 环境检测、版本匹配与自动安装。

替代旧版 ``bin/export/Examine.py`` 的 Java 部分、``bin/export/Java.py``
以及 bootstrap 中的 Java 初始化逻辑。

修复的旧版 bug：
- 版本区间缺口（1.17.0 / 1.20.5 / >1.21.8 无匹配）
- ``version == 1.8`` 浮点比较导致字符串 '1.8' 不命中
- 正则只匹配三段式版本号（'17' 匹配失败）
- 目录前缀误匹配（jdk1.8 被当成 jdk16 的候选）
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import requests
from packaging.version import Version, InvalidVersion

from omniark.core import paths
from omniark.core.logger import get_logger
from omniark.exceptions import JavaNotFoundError, DownloadError

logger = get_logger()

# MC 版本 -> 所需 Java 大版本（区间下界闭、上界开，按规则顺序匹配）
_JAVA_RULES: list[tuple[str, str]] = [
    ("1.20.5", "21"),
    ("1.18", "17"),
    ("1.17", "16"),
    ("0", "1.8"),
]

# Java 大版本 -> Amazon Corretto 下载地址（Windows x64 zip）
CORRETTO_URLS = {
    "1.8": "https://corretto.aws/downloads/latest/amazon-corretto-8-x64-windows-jdk.zip",
    "16": "https://corretto.aws/downloads/latest/amazon-corretto-16-x64-windows-jdk.zip",
    "17": "https://corretto.aws/downloads/latest/amazon-corretto-17-x64-windows-jdk.zip",
    "21": "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-windows-jdk.zip",
    "25": "https://corretto.aws/downloads/latest/amazon-corretto-25-x64-windows-jdk.zip",
}

# class 文件主版本号与 Java 大版本的偏移（52 -> Java 8, 65 -> Java 21, 69 -> Java 25）
_CLASS_MAJOR_OFFSET = 44
# 检测 jar 时最多读取的 .class 条目数（防爆）
_JAR_SCAN_LIMIT = 4000

JAVA_VERSIONS_FILE = "java_versions.json"

_VERSION_RE = re.compile(r'version "([^"]+)"')


# ------------------------------------------------------------ 版本解析

def parse_version(version_str: str) -> list[int]:
    """把 '1.8.0_452' / '17.0.7+7' 解析为 [1,8,0,452] / [17,0,7]。"""
    cleaned = re.sub(r"[^\d.]", "", version_str.split("+")[0].replace("_", "."))
    return [int(x) for x in cleaned.split(".") if x != ""]


def required_java_for_minecraft(mc_version: str) -> str:
    """根据 Minecraft 版本返回所需 Java 大版本（'1.8'/'16'/'17'/'21'）。"""
    try:
        mc = Version(mc_version)
    except InvalidVersion:
        logger.warning("无法解析的 Minecraft 版本: %s，回退 Java 17", mc_version)
        return "17"
    for bound, java in _JAVA_RULES:
        if mc >= Version(bound):
            return java
    return "1.8"


# ------------------------------------------------------------ 检测

def find_java_installations() -> list[Path]:
    """扫描系统中所有 java.exe（Windows 为主，兼容常见 Unix 路径）。"""
    candidates: list[Path] = []
    if sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        java_root = Path(program_files) / "Java"
        if java_root.is_dir():
            candidates.extend(java_root.glob("*/bin/java.exe"))
    else:
        for base in ("/usr/lib/jvm", "/usr/java",
                     "/Library/Java/JavaVirtualMachines",
                     str(Path.home() / ".sdkman/candidates/java")):
            base_path = Path(base)
            if base_path.is_dir():
                for p in base_path.rglob("java"):
                    if p.is_file() and "bin" in p.parts:
                        candidates.append(p)
    # 去重并保持顺序
    seen: set[str] = set()
    result: list[Path] = []
    for c in candidates:
        key = str(c).lower()
        if key not in seen:
            seen.add(key)
            result.append(c)
    return result


def java_version(java_path: str | Path) -> str | None:
    """获取指定 java 的版本字符串（读 stderr，5 秒超时）。"""
    try:
        proc = subprocess.run(
            [str(java_path), "-version"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _VERSION_RE.search(proc.stderr or "")
    return match.group(1) if match else None


def version_match(target: str, installed: str, exact: bool = False) -> bool:
    """判断已安装版本是否满足目标版本（按数字段比较公共前缀）。"""
    target_parts = parse_version(target)
    installed_parts = parse_version(installed)
    if exact:
        return installed_parts[: len(target_parts)] == target_parts
    return bool(installed_parts) and installed_parts[0] == target_parts[0] \
        if len(target_parts) == 1 else \
        installed_parts[: len(target_parts)] == target_parts


def find_matching_java(target_version: str,
                       extra_paths: list[str | Path] | None = None,
                       exact: bool = False) -> dict[str, str]:
    """返回 {java路径: 实际版本} 的匹配结果字典。"""
    candidates = find_java_installations()
    if extra_paths:
        candidates.extend(Path(p) for p in extra_paths)
    matched: dict[str, str] = {}
    for candidate in candidates:
        ver = java_version(candidate)
        if ver and version_match(target_version, ver, exact):
            matched[str(candidate)] = ver
    return matched


# ------------------------------------------------------------ jar 检测（自动纠正核心）

def jar_required_java_major(jar_path: str | Path) -> int | None:
    """读取 jar 内 .class 文件的最高主版本号，返回所需 Java 大版本。

    class 主版本 = Java 大版本 + 44（如 65 -> Java 21，69 -> Java 25）。
    无法解析时返回 None。
    """
    jar = Path(jar_path)
    if not jar.is_file():
        return None
    majors: list[int] = []
    try:
        with zipfile.ZipFile(jar) as zf:
            names = [n for n in zf.namelist() if n.endswith(".class")]
            for name in names[:_JAR_SCAN_LIMIT]:
                try:
                    with zf.open(name) as f:
                        header = f.read(8)
                except (OSError, KeyError, zipfile.BadZipFile):
                    continue
                if len(header) == 8 and header[:4] == b"\xca\xfe\xba\xbe":
                    majors.append(int.from_bytes(header[6:8], "big"))
    except (OSError, zipfile.BadZipFile) as exc:
        logger.warning("读取 jar 失败 %s: %s", jar, exc)
        return None
    if not majors:
        return None
    return max(majors) - _CLASS_MAJOR_OFFSET


def required_java_for_server(core_path: str | Path,
                             mc_version: str) -> tuple[str, str]:
    """综合 MC 版本规则与 jar 实测，返回 (所需 Java 大版本, 判定来源)。

    取两者中的较大值——MC 版本规则可能滞后于新版本发布，
    jar 实测是最可靠的依据。
    """
    rule = required_java_for_minecraft(mc_version)
    rule_major = parse_version(rule)[0] if rule != "1.8" else 8
    jar_major = jar_required_java_major(core_path)
    if jar_major is not None and jar_major > rule_major:
        return str(jar_major), f"jar 实测（class 版本 {jar_major + _CLASS_MAJOR_OFFSET}）"
    return rule, f"MC {mc_version} 版本规则"


def resolve_java_for_server(core_path: str | Path,
                            mc_version: str,
                            root: Path | None = None) -> tuple[str, str]:
    """为服务器找到满足要求的 java.exe，自动纠正版本不符的配置。

    返回 (java 路径, 判定来源)。找不到时抛 JavaNotFoundError（附带建议）。
    """
    required, source = required_java_for_server(core_path, mc_version)
    required_major = int(required) if required != "1.8" else 8

    mapping = load_java_versions(root)
    configured = mapping.get(required, "")
    if configured and Path(configured).is_file():
        ver = java_version(configured)
        if ver and _java_major(ver) >= required_major:
            return configured, source
        logger.warning("配置的 Java (%s) 版本 %s 不满足所需 %s，自动纠正",
                       configured, ver, required)

    # 系统扫描 + 已配置的其他路径都参与匹配
    extra = [p for p in mapping.values() if p]
    matched = find_matching_java(required, extra_paths=extra)
    if matched:
        java_path = next(iter(matched))
        mapping[required] = java_path
        save_java_versions(mapping, root)
        logger.info("已自动选择 Java %s: %s（%s）", required, java_path, source)
        return java_path, source

    raise JavaNotFoundError(
        f"未找到满足要求的 Java {required}+（核心 {Path(core_path).name} 需要，"
        f"判定依据：{source}）。请在 Java 管理器中添加路径或安装后重试")


def _java_major(version_str: str) -> int:
    """'1.8.0_452' -> 8；'17.0.7' -> 17。"""
    parts = parse_version(version_str)
    if not parts:
        return 0
    return parts[1] if parts[0] == 1 and len(parts) > 1 else parts[0]


# ------------------------------------------------------------ java_versions.json

def load_java_versions(root: Path | None = None) -> dict[str, str]:
    """读取 java_versions.json（{大版本: java.exe 路径}，保留全部已有键）。"""
    file = (root or paths.workspace_root()) / JAVA_VERSIONS_FILE
    default = {key: "" for key in CORRETTO_URLS}
    if not file.exists():
        return default
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error("java_versions.json 损坏，重建")
        return default
    default.update({str(k): str(v) for k, v in data.items()})
    return default


def save_java_versions(mapping: dict[str, str], root: Path | None = None) -> None:
    file = (root or paths.workspace_root()) / JAVA_VERSIONS_FILE
    file.write_text(json.dumps(mapping, indent=4, ensure_ascii=False),
                    encoding="utf-8")


def resolve_java_for_minecraft(mc_version: str,
                               root: Path | None = None) -> str:
    """为指定 MC 版本找到可用的 java.exe 路径。

    依次尝试：java_versions.json 配置 → 系统扫描。找不到抛 JavaNotFoundError。
    """
    required = required_java_for_minecraft(mc_version)
    mapping = load_java_versions(root)
    configured = mapping.get(required, "")
    if configured and Path(configured).is_file():
        return configured

    matched = find_matching_java(required)
    if matched:
        java_path = next(iter(matched))
        mapping[required] = java_path
        save_java_versions(mapping, root)
        return java_path

    raise JavaNotFoundError(
        f"未找到 Java {required}（Minecraft {mc_version} 需要），"
        f"请先安装或运行 java 自动安装")


# ------------------------------------------------------------ 自动安装

def install_java_windows(version: str, retries: int = 5) -> str:
    """在 Windows 上自动安装 Amazon Corretto JDK，返回 java.exe 路径。

    需要管理员权限（写入 Program Files 与系统环境变量）。
    """
    version = str(version)
    url = CORRETTO_URLS.get(version)
    if url is None:
        raise JavaNotFoundError(f"不支持自动安装的 Java 版本: {version}")
    if sys.platform != "win32":
        raise JavaNotFoundError("自动安装仅支持 Windows")

    zip_path = Path(tempfile.gettempdir()) / f"jdk{version}_installer.zip"
    _download_with_retry(url, zip_path, retries)

    install_root = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Java"
    install_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(install_root)

    # 精确匹配顶层目录：jdk1.8.0_xxx / jdk16.x / jdk17.x / jdk21.x
    prefix = "jdk1.8" if version == "1.8" else f"jdk{version}."
    candidates = sorted(
        (d for d in install_root.iterdir()
         if d.is_dir() and d.name.lower().startswith(prefix)),
        key=lambda d: d.stat().st_mtime, reverse=True)
    if not candidates:
        raise JavaNotFoundError(f"解压后未找到 JDK {version} 目录")
    jdk_dir = candidates[0]

    java_exe = jdk_dir / "bin" / "java.exe"
    javac_exe = jdk_dir / "bin" / "javac.exe"
    if not java_exe.is_file() or not javac_exe.is_file():
        raise JavaNotFoundError(f"JDK 目录不完整: {jdk_dir}")
    if java_version(java_exe) is None:
        raise JavaNotFoundError(f"Java 安装验证失败: {java_exe}")

    _set_java_env(jdk_dir)
    logger.info("Java %s 安装完成: %s", version, java_exe)
    return str(java_exe)


def _download_with_retry(url: str, dest: Path, retries: int) -> None:
    headers = {"User-Agent": "Mozilla/5.0"}
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=60,
                              headers=headers) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                if total and downloaded != total:
                    raise DownloadError(
                        f"下载不完整: {downloaded}/{total} 字节")
            return
        except (requests.RequestException, DownloadError, OSError) as exc:
            last_error = exc
            logger.warning("Java 下载第 %d 次失败: %s", attempt, exc)
    raise DownloadError(f"Java 下载失败（重试 {retries} 次）: {last_error}")


def _set_java_env(jdk_dir: Path) -> None:
    """写入系统环境变量（需管理员权限）。

    注意：不使用旧版 ``setx PATH "%PATH%;..." /M`` 的做法（1024 字符截断
    风险），改为通过注册表读取系统 PATH 后追加。
    """
    if sys.platform != "win32":
        return
    import winreg

    try:
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "JAVA_HOME", 0,
                              winreg.REG_SZ, str(jdk_dir))
            try:
                sys_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                sys_path = ""
            bin_dir = str(jdk_dir / "bin")
            entries = [e for e in sys_path.split(";") if e]
            if bin_dir.lower() not in {e.lower() for e in entries}:
                entries.append(bin_dir)
                winreg.SetValueEx(key, "Path", 0,
                                  winreg.REG_EXPAND_SZ, ";".join(entries))
    except PermissionError as exc:
        raise JavaNotFoundError(
            "写入系统环境变量需要管理员权限，请手动配置 JAVA_HOME") from exc
