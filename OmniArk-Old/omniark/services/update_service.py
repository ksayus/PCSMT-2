"""程序自动更新（GitHub/Gitee 双源）。

替代旧版 ``bin/download/Update.py``。

修复的旧版 bug：
- GitHub 请求 verify=False 关闭证书校验
- Gitee 分支 download_url 可能未定义（UnboundLocalError）
- 返回值 True/False/None 语义混乱 → 改为明确的 UpdateResult 枚举
- os.system('powershell curl ...') 下载 → requests
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path

import requests
from packaging.version import Version, InvalidVersion

from omniark.core import paths
from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.exceptions import DownloadError
from omniark.services.core_downloader import download_file

logger = get_logger()


class UpdateStatus(enum.Enum):
    UP_TO_DATE = "up_to_date"       # 已是最新
    UPDATE_AVAILABLE = "available"  # 有新版本（未下载）
    DOWNLOADED = "downloaded"       # 新版本已下载
    FAILED = "failed"               # 检查/下载失败


@dataclass
class UpdateResult:
    status: UpdateStatus
    source: str = ""
    latest_version: str = ""
    download_path: Path | None = None
    message: str = ""


def check_update(source: str | None = None) -> UpdateResult:
    """检查更新（不下载）。

    :param source: 'Github'/'Gitee'；None 时读配置，首选源失败自动回退。
    """
    cfg = get_config()
    sources = [source] if source else _ordered_sources(cfg.AutoUpdateSource)

    last_error = ""
    for src in sources:
        try:
            release = _fetch_latest_release(src)
            tag = release["tag_name"].lstrip("vV")
            local = cfg.PCSMT2_Version.lstrip("vV")
            try:
                newer = Version(tag) > Version(local)
            except InvalidVersion:
                logger.warning("无法比较版本号: 本地 %s vs 远端 %s", local, tag)
                newer = tag != local
            if not newer:
                return UpdateResult(UpdateStatus.UP_TO_DATE, source=src,
                                    latest_version=tag, message="已是最新版本")
            return UpdateResult(UpdateStatus.UPDATE_AVAILABLE, source=src,
                                latest_version=tag,
                                message=f"发现新版本: {tag}")
        except UpdateCheckError as exc:
            last_error = str(exc)
            logger.warning("从 %s 检查更新失败: %s", src, exc)
    return UpdateResult(UpdateStatus.FAILED, message=last_error or "检查更新失败")


def download_update(root: Path | None = None,
                    source: str | None = None) -> UpdateResult:
    """检查并下载最新版本安装包到工作目录。"""
    root = root or paths.workspace_root()
    result = check_update(source)
    if result.status is not UpdateStatus.UPDATE_AVAILABLE:
        return result
    try:
        release = _fetch_latest_release(result.source)
        url = _pick_asset_url(result.source, release)
        if url is None:
            return UpdateResult(UpdateStatus.FAILED, source=result.source,
                                latest_version=result.latest_version,
                                message="发布中没有可下载的资源")
        name = release.get("name") or f"update-{result.latest_version}"
        if not name.lower().endswith(".exe"):
            name += ".exe"
        dest = download_file(url, root / name)
        return UpdateResult(UpdateStatus.DOWNLOADED, source=result.source,
                            latest_version=result.latest_version,
                            download_path=dest, message="新版本下载完成")
    except UpdateCheckError as exc:
        return UpdateResult(UpdateStatus.FAILED, source=result.source,
                            message=f"下载更新失败: {exc}")
    except DownloadError as exc:
        return UpdateResult(UpdateStatus.FAILED, source=result.source,
                            message=f"下载更新失败: {exc}")


class UpdateCheckError(Exception):
    """更新检查失败。"""


def _ordered_sources(preferred: str) -> list[str]:
    preferred = (preferred or "Github").capitalize()
    sources = ["Github", "Gitee"]
    if preferred in sources:
        sources.remove(preferred)
        sources.insert(0, preferred)
    return sources


def _fetch_latest_release(source: str) -> dict:
    url = paths.REPOSITORY_API.get(source.lower())
    if url is None:
        raise UpdateCheckError(f"未知的更新源: {source}")
    try:
        resp = requests.get(url, timeout=15)  # 不再关闭证书校验
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise UpdateCheckError(f"请求失败: {exc}") from exc
    if "tag_name" not in data:
        raise UpdateCheckError("响应中没有 tag_name")
    return data


def _pick_asset_url(source: str, release: dict) -> str | None:
    assets = release.get("assets", [])
    if source == "Github":
        return assets[0].get("browser_download_url") if assets else None
    # Gitee：找第一个 .exe 资源
    for asset in assets:
        name = asset.get("name", "")
        if name.endswith(".exe"):
            return asset.get("browser_download_url")
    return None
