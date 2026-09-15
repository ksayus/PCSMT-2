"""服务器核心下载与安装（official/forge/fabric/mohist）。

替代旧版 ``bin/download/Core.py`` 与 ``CoreInstaller.py``，
所有下载统一走 requests（替代 os.system('powershell curl ...')），
安装调用走 subprocess 参数列表（杜绝 shell 注入）。
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import requests

from omniark.core import paths
from omniark.core.logger import get_logger
from omniark.exceptions import DownloadError, VersionNotFoundError
from omniark.services import minecraft_versions
from omniark.services.java_service import resolve_java_for_minecraft

logger = get_logger()

CORE_TYPES = ("official", "forge", "fabric", "mohist")

FORGE_PROMOTIONS_URL = ("https://files.minecraftforge.net/net/minecraftforge/"
                        "forge/promotions_slim.json")
FORGE_MAVEN_URL = ("https://maven.minecraftforge.net/net/minecraftforge/forge/"
                   "{mc}-{forge}/forge-{mc}-{forge}-installer.jar")
FABRIC_INSTALLER_VERSION = "1.0.1"
FABRIC_INSTALLER_URL = (
    "https://maven.fabricmc.net/net/fabricmc/fabric-installer/"
    f"{FABRIC_INSTALLER_VERSION}/fabric-installer-{FABRIC_INSTALLER_VERSION}.jar")
MOHIST_BUILDS_URL = "https://mohistmc.com/api/v2/projects/mohist/{version}/builds"


# ------------------------------------------------------------ 通用下载

def download_file(url: str, dest: str | Path, retries: int = 3,
                  timeout: int = 60) -> Path:
    """下载文件（requests 流式 + 重试 + 进度日志），替代 powershell curl。"""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=64 * 1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            if pct % 25 == 0:
                                logger.debug("下载进度 %d%% (%s)", pct, dest.name)
                if total and downloaded != total:
                    raise DownloadError(
                        f"下载不完整: {downloaded}/{total} 字节")
            logger.info("下载完成: %s -> %s", url, dest)
            return dest
        except (requests.RequestException, DownloadError, OSError) as exc:
            last_error = exc
            logger.warning("下载第 %d/%d 次失败: %s", attempt, retries, exc)
            time.sleep(min(attempt * 2, 10))
    raise DownloadError(f"下载失败（重试 {retries} 次）: {url} — {last_error}")


# ------------------------------------------------------------ 各核心下载

def download_core(server_name: str, core_type: str, mc_version: str,
                  root: Path | None = None) -> Path:
    """下载并安装指定类型的服务器核心，返回核心文件路径。

    :raises ValueError: 核心类型不支持。
    :raises DownloadError/VersionNotFoundError: 下载失败。
    """
    core_type = core_type.lower()
    server_dir = paths.servers_dir(root) / server_name
    server_dir.mkdir(parents=True, exist_ok=True)

    if core_type == "official":
        return _download_official(server_dir, mc_version)
    if core_type == "forge":
        return _download_forge(server_dir, mc_version, root)
    if core_type == "fabric":
        return _download_fabric(server_dir, mc_version, root)
    if core_type == "mohist":
        return _download_mohist(server_dir, mc_version)
    raise ValueError(f"不支持的核心类型: {core_type}（可选: {CORE_TYPES}）")


def _download_official(server_dir: Path, mc_version: str) -> Path:
    url = minecraft_versions.get_server_download_url(mc_version)
    dest = server_dir / paths.CORE_DEFAULT_NAMES["official"]
    return download_file(url, dest)


def _download_forge(server_dir: Path, mc_version: str,
                    root: Path | None) -> Path:
    forge_build = _resolve_forge_build(mc_version)
    installer_url = FORGE_MAVEN_URL.format(mc=mc_version, forge=forge_build)
    installer = paths.core_installation_dir(root) / paths.INSTALLER_FILES["forge"]
    if not installer.exists():
        download_file(installer_url, installer)

    java = resolve_java_for_minecraft(mc_version, root)
    logger.info("开始安装 Forge %s-%s 到 %s", mc_version, forge_build, server_dir)
    proc = subprocess.run(
        [java, "-jar", str(installer), "--installServer", str(server_dir)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise DownloadError(f"Forge 安装失败: {proc.stderr[-500:]}")

    # 安装完成后定位 forge 服务端 jar（形如 forge-<mc>-<build>.jar / -shim.jar）
    jars = sorted(server_dir.glob("forge-*.jar"))
    jars = [j for j in jars if "installer" not in j.name]
    if not jars:
        raise DownloadError("Forge 安装完成但未找到服务端 jar")
    return jars[0]


def _download_fabric(server_dir: Path, mc_version: str,
                     root: Path | None) -> Path:
    installer = paths.core_installation_dir(root) / paths.INSTALLER_FILES["fabric"]
    if not installer.exists():
        download_file(FABRIC_INSTALLER_URL, installer)

    java = resolve_java_for_minecraft(mc_version, root)
    logger.info("开始安装 Fabric %s 到 %s", mc_version, server_dir)
    proc = subprocess.run(
        [java, "-jar", str(installer), "server",
         "-mcversion", mc_version, "-downloadMinecraft",
         "-dir", str(server_dir)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise DownloadError(f"Fabric 安装失败: {proc.stderr[-500:]}")

    launch_jar = server_dir / paths.CORE_DEFAULT_NAMES["fabric"]
    if not launch_jar.exists():
        raise DownloadError("Fabric 安装完成但未找到 fabric-server-launch.jar")
    return launch_jar


def _download_mohist(server_dir: Path, mc_version: str) -> Path:
    url = MOHIST_BUILDS_URL.format(version=mc_version)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        builds = resp.json().get("builds", [])
    except (requests.RequestException, ValueError) as exc:
        raise DownloadError(f"获取 Mohist 构建列表失败: {exc}") from exc
    if not builds:
        raise VersionNotFoundError(f"Mohist 没有 {mc_version} 的构建")
    download_url = builds[-1].get("url")
    if not download_url:
        raise DownloadError("Mohist 构建信息中没有下载地址")
    dest = server_dir / paths.CORE_DEFAULT_NAMES["mohist"]
    return download_file(download_url, dest)


def _resolve_forge_build(mc_version: str) -> str:
    """从 promotions_slim.json 解析指定 MC 版本的最新 Forge 构建号。"""
    try:
        resp = requests.get(FORGE_PROMOTIONS_URL, timeout=15)
        resp.raise_for_status()
        promos = resp.json().get("promos", {})
    except (requests.RequestException, ValueError) as exc:
        raise DownloadError(f"获取 Forge 版本清单失败: {exc}") from exc
    build = promos.get(f"{mc_version}-latest") or promos.get(f"{mc_version}-recommended")
    if not build:
        raise VersionNotFoundError(f"Forge 不支持 Minecraft {mc_version}")
    return build
