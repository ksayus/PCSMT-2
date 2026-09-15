"""服务器备份与回档服务（替代旧版 Processing.Retracement）。

旧版问题：126 行复制粘贴×4、old-save.zip 循环内 'w' 模式重建只留最后
一个条目、arcname 用绝对路径、ebackup 大小写匹配失败。这里统一为一次
遍历：先把现有内容打包到 old-save.zip（相对路径），再删除，最后解压备份。

支持的备份来源：
- OmniArk 原生备份：<服务器>/omniark_backups/*.zip（可手动创建，
  回档前也会自动备份当前存档）
- FTB Backups 2 模组：<服务器>/backups/*.zip
- eBackup 插件：<服务器>/plugins/eBackup/backups/*.zip
"""

from __future__ import annotations

import shutil
import stat
import zipfile
from datetime import datetime
from pathlib import Path

from omniark.core.logger import get_logger
from omniark.exceptions import BackupError, BackupNotFoundError
from omniark.services import registry
from omniark.utils.formatting import human_readable_size

logger = get_logger()

NATIVE_BACKUP_DIR = "omniark_backups"
FTB_BACKUP_DIR = "backups"
EBACKUP_DIR = "plugins/eBackup/backups"
OLD_SAVE_ZIP = "old-save.zip"

# 原生备份包含的世界目录（存在才打包）
_WORLD_DIRS = ("world", "world_nether", "world_the_end")
# 整目录备份时排除的目录名
_BACKUP_EXCLUDE = {"logs", "cache", "libraries", NATIVE_BACKUP_DIR,
                   FTB_BACKUP_DIR, "plugins"}


# ------------------------------------------------------------ 统一列表

def list_backups(server_name: str,
                 root: Path | None = None) -> list[dict[str, str]]:
    """统一列出全部来源的备份（按时间升序）。

    每项：{name, source, size, mtime}；source ∈ native/mod/plugin。
    """
    server = registry.load_server(server_name, root)
    result: list[dict[str, str]] = []
    for directory, source in (
            (server.directory / NATIVE_BACKUP_DIR, "native"),
            (server.directory / FTB_BACKUP_DIR, "mod"),
            (server.directory / EBACKUP_DIR, "plugin")):
        if not directory.is_dir():
            continue
        for z in _sorted_zips(directory):
            st = z.stat()
            result.append({
                "name": z.name,
                "source": source,
                "size": human_readable_size(st.st_size),
                "mtime": datetime.fromtimestamp(
                    st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return sorted(result, key=lambda item: item["mtime"])


# ------------------------------------------------------------ 原生备份

def create_backup(server_name: str, root: Path | None = None,
                  note: str = "") -> Path:
    """手动创建原生备份：打包世界目录（无世界目录时打包整目录去排除项）。

    :return: 生成的备份 zip 路径。
    """
    server = registry.load_server(server_name, root)
    backup_dir = server.directory / NATIVE_BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{note}" if note else ""
    backup_path = backup_dir / f"backup_{stamp}{suffix}.zip"

    worlds = [server.directory / w for w in _WORLD_DIRS
              if (server.directory / w).is_dir()]
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if worlds:
            for world in worlds:
                for file in world.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(server.directory))
        else:
            for item in server.directory.iterdir():
                if item.name in _BACKUP_EXCLUDE or item.name == OLD_SAVE_ZIP:
                    continue
                if item.is_dir():
                    for file in item.rglob("*"):
                        if file.is_file():
                            zf.write(file, file.relative_to(server.directory))
                elif item.is_file():
                    zf.write(item, item.name)
    logger.info("服务器 %s 原生备份已创建: %s", server_name, backup_path.name)
    return backup_path


def delete_backup(server_name: str, backup_file: str,
                  root: Path | None = None) -> None:
    """删除指定备份文件（按文件名在所有来源目录中匹配，防目录穿越）。"""
    server = registry.load_server(server_name, root)
    safe_name = Path(backup_file).name
    for directory in (server.directory / NATIVE_BACKUP_DIR,
                      server.directory / FTB_BACKUP_DIR,
                      server.directory / EBACKUP_DIR):
        target = directory / safe_name
        if target.is_file():
            target.unlink()
            logger.info("备份已删除: %s", target)
            return
    raise BackupNotFoundError(f"备份文件不存在: {backup_file}")


# ------------------------------------------------------------ 回档

def find_backups(server_name: str,
                 root: Path | None = None) -> tuple[list[Path], str]:
    """查找可用备份，返回 (按时间排序的备份列表, 来源 'native'/'mod'/'plugin')。

    优先级：原生备份 → FTB 模组 → eBackup 插件。
    :raises BackupNotFoundError: 没有找到任何备份。
    """
    server = registry.load_server(server_name, root)

    native_dir = server.directory / NATIVE_BACKUP_DIR
    if native_dir.is_dir():
        backups = _sorted_zips(native_dir)
        if backups:
            return backups, "native"

    mod_backup_dir = server.directory / FTB_BACKUP_DIR
    if _has_ftb_mod(server) and mod_backup_dir.is_dir():
        backups = _sorted_zips(mod_backup_dir)
        if backups:
            return backups, "mod"

    plugin_backup_dir = server.directory / EBACKUP_DIR
    if plugin_backup_dir.is_dir():
        backups = _sorted_zips(plugin_backup_dir)
        if backups:
            return backups, "plugin"

    raise BackupNotFoundError(
        f"服务器 {server_name} 没有可用备份（可在备份管理中手动创建，"
        f"或使用 FTB Backups 2 模组 / eBackup 插件）")


def restore_backup(server_name: str, backup_file: str | None = None,
                   root: Path | None = None,
                   auto_backup: bool = True) -> Path:
    """回档服务器。

    :param backup_file: 备份文件名（跨所有来源目录匹配）；None 时用最新。
    :param auto_backup: 回档前自动备份当前存档到 omniark_backups/
        （文件名带 pre-restore 标记，防止误操作丢档）。
    :return: 使用的备份文件路径。
    """
    server = registry.load_server(server_name, root)
    backups, source = find_backups(server_name, root)

    if backup_file is None:
        backup_path = backups[-1]  # 已按时间排序，取最新
        logger.info("未指定备份文件，使用最新: %s", backup_path.name)
    else:
        safe_name = Path(backup_file).name  # 防目录穿越
        matched = [b for b in backups if b.name == safe_name]
        if not matched:
            # find_backups 只返回一个来源，跨来源再查一次
            matched = [p for d in (NATIVE_BACKUP_DIR, FTB_BACKUP_DIR,
                                   EBACKUP_DIR)
                       if (p := server.directory / d / safe_name).is_file()]
        if not matched:
            raise BackupNotFoundError(f"备份文件不存在: {backup_file}")
        backup_path = matched[0]

    if not zipfile.is_zipfile(backup_path):
        raise BackupError(f"备份文件不是有效的 zip: {backup_path}")

    # 0. 回档前自动备份当前存档（防误操作丢档）
    if auto_backup:
        try:
            pre = create_backup(server_name, root, note="pre-restore")
            logger.info("回档前存档已自动备份: %s", pre.name)
        except (BackupError, OSError) as exc:
            logger.warning("回档前自动备份失败（继续回档）: %s", exc)

    with zipfile.ZipFile(backup_path) as zf:
        top_entries = _top_level_entries(zf)

    # 1. 把将被覆盖的现有内容打包保存到 old-save.zip（一次写入，相对路径）
    old_save = server.directory / OLD_SAVE_ZIP
    saved_anything = False
    with zipfile.ZipFile(old_save, "w", zipfile.ZIP_DEFLATED) as zf:
        for entry in top_entries:
            existing = server.directory / entry
            if existing.is_dir():
                for file in existing.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(server.directory))
                        saved_anything = True
            elif existing.is_file():
                zf.write(existing, existing.relative_to(server.directory))
                saved_anything = True
    if saved_anything:
        logger.info("现有数据已保存到 %s", old_save)
    else:
        old_save.unlink(missing_ok=True)

    # 2. 删除将被覆盖的现有内容
    for entry in top_entries:
        target = server.directory / entry
        if target.is_dir():
            shutil.rmtree(target, onerror=_remove_readonly)
            logger.info("已删除旧目录: %s", entry)
        elif target.is_file():
            target.unlink()
            logger.info("已删除旧文件: %s", entry)

    # 3. 解压备份
    with zipfile.ZipFile(backup_path) as zf:
        zf.extractall(server.directory)
    logger.info("服务器 %s 已从 %s 回档完成", server_name, backup_path.name)
    return backup_path


# ------------------------------------------------------------ 内部工具

def _has_ftb_mod(server) -> bool:
    mods_dir = server.mods_dir
    if not mods_dir.is_dir():
        return False
    return any("ftbbackups2" in p.name.lower() for p in mods_dir.iterdir())


def _sorted_zips(directory: Path) -> list[Path]:
    zips = [p for p in directory.iterdir()
            if p.is_file() and p.suffix == ".zip"]
    return sorted(zips, key=lambda p: p.stat().st_mtime)


def _top_level_entries(zf: zipfile.ZipFile) -> list[str]:
    """备份 zip 中的首级条目（目录或独立文件）。"""
    tops: set[str] = set()
    for name in zf.namelist():
        first = name.split("/")[0]
        if first:
            tops.add(first)
    return sorted(tops)


def _remove_readonly(func, path, _exc_info) -> None:
    import os
    os.chmod(path, stat.S_IWRITE)
    func(path)
