"""Minecraft 版本清单获取（替代旧版 Get.Info.MinecraftVersion）。

旧版在 import 时发起网络请求并缓存到全局类属性；这里改为显式函数调用 +
可选内存缓存，接口层自行决定何时调用。
"""

from __future__ import annotations

import time

import requests

from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.exceptions import DownloadError

logger = get_logger()

VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
# 旧版地址（v1 manifest），保留作为回退
LEGACY_MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

# 快照/测试版标识（旧版按子串黑名单过滤，这里保留同样的过滤语义）
_SNAPSHOT_KEYWORDS = (
    "w", "a", "b", "c", "rd", "rc", "craftmine", "inf", "pre",
    "1.RV-Pre1", "3D", "Shareware", "Pre-release",
)

_cache: dict[str, tuple[float, list[str]]] = {}
_CACHE_TTL = 600  # 10 分钟


def fetch_minecraft_versions(include_snapshots: bool | None = None,
                             use_cache: bool = True) -> list[str]:
    """获取 Minecraft 版本 id 列表。

    :param include_snapshots: 是否包含快照/测试版；None 时读配置
        ``MinecraftTestVersion``。
    :raises DownloadError: 网络请求失败。
    """
    if include_snapshots is None:
        include_snapshots = get_config().MinecraftTestVersion

    cache_key = "all" if include_snapshots else "release"
    if use_cache and cache_key in _cache:
        ts, versions = _cache[cache_key]
        if time.time() - ts < _CACHE_TTL:
            return versions

    data = _fetch_manifest()
    ids = [v.get("id", "") for v in data.get("versions", []) if v.get("id")]
    if not include_snapshots:
        ids = [v for v in ids if not _is_snapshot(v)]

    _cache[cache_key] = (time.time(), ids)
    logger.debug("获取 Minecraft 版本列表成功，共 %d 个", len(ids))
    return ids


def get_server_download_url(mc_version: str) -> str:
    """获取官方服务端 jar 的下载地址。

    :raises VersionNotFoundError: 版本不存在或该版本无服务端下载。
    """
    from omniark.exceptions import VersionNotFoundError

    data = _fetch_manifest()
    entry = next((v for v in data.get("versions", [])
                  if v.get("id") == mc_version), None)
    if entry is None:
        raise VersionNotFoundError(f"Minecraft 版本不存在: {mc_version}")
    try:
        detail = requests.get(entry["url"], timeout=15).json()
        return detail["downloads"]["server"]["url"]
    except (KeyError, requests.RequestException, ValueError) as exc:
        raise VersionNotFoundError(
            f"版本 {mc_version} 没有可用的服务端下载") from exc


def _fetch_manifest() -> dict:
    try:
        resp = requests.get(VERSION_MANIFEST_URL, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise DownloadError(f"获取 Minecraft 版本清单失败: {exc}") from exc


def _is_snapshot(version_id: str) -> bool:
    return any(keyword in version_id for keyword in _SNAPSHOT_KEYWORDS)
