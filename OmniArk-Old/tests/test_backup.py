"""备份服务测试：原生备份创建 / 统一列表 / 回档前自动备份 / 删除。"""

import zipfile
from pathlib import Path

import pytest

from omniark.exceptions import BackupNotFoundError
from omniark.models.server import ServerInstance
from omniark.services import backup_service, registry


@pytest.fixture()
def server(tmp_path):
    """在隔离工作目录伪造一台带 world 的服务器。"""
    server_dir = tmp_path / "servers" / "svr1"
    (server_dir / "world" / "region").mkdir(parents=True)
    (server_dir / "world" / "level.dat").write_bytes(b"leveldata")
    (server_dir / "world" / "region" / "r.0.0.mca").write_bytes(b"chunk")
    (server_dir / "server.properties").write_text("server-port=25565\n")
    instance = ServerInstance(
        Name="svr1", Counts=1, Core="core.jar", Path=str(server_dir),
        StartBatchPath=str(server_dir / "start.bat"), Size="1MB",
        Version="1.21", LatestStartedTime="", CoreType="official")
    instance.save(tmp_path)
    return instance


def test_create_backup_zips_world(server, tmp_path):
    backup = backup_service.create_backup("svr1", tmp_path)
    assert backup.is_file()
    with zipfile.ZipFile(backup) as zf:
        names = zf.namelist()
    assert "world/level.dat" in names
    assert "world/region/r.0.0.mca" in names
    # 只打包世界目录，不含 server.properties
    assert "server.properties" not in names


def test_list_backups_unified(server, tmp_path):
    backup_service.create_backup("svr1", tmp_path)
    backups = backup_service.list_backups("svr1", tmp_path)
    assert len(backups) == 1
    assert backups[0]["source"] == "native"
    assert backups[0]["name"].startswith("backup_")


def test_restore_with_auto_pre_backup(server, tmp_path):
    """回档前自动备份当前存档（pre-restore）。"""
    # 先做一次备份，然后修改存档
    backup_service.create_backup("svr1", tmp_path)
    (Path(server.Path) / "world" / "level.dat").write_bytes(b"modified")
    # 回档（auto_backup 默认开）
    used = backup_service.restore_backup("svr1", root=tmp_path)
    assert used.is_file()
    # 存档内容恢复
    assert (Path(server.Path) / "world" / "level.dat").read_bytes() \
        == b"leveldata"
    # 自动生成了 pre-restore 备份
    backups = backup_service.list_backups("svr1", tmp_path)
    assert any("pre-restore" in b["name"] for b in backups)


def test_restore_specific_backup(server, tmp_path):
    b1 = backup_service.create_backup("svr1", tmp_path)
    used = backup_service.restore_backup("svr1", b1.name, root=tmp_path,
                                         auto_backup=False)
    assert used.name == b1.name


def test_restore_missing_backup(server, tmp_path):
    backup_service.create_backup("svr1", tmp_path)
    with pytest.raises(BackupNotFoundError):
        backup_service.restore_backup("svr1", "ghost.zip", root=tmp_path,
                                      auto_backup=False)


def test_delete_backup(server, tmp_path):
    backup = backup_service.create_backup("svr1", tmp_path)
    backup_service.delete_backup("svr1", backup.name, tmp_path)
    assert not backup.is_file()
    with pytest.raises(BackupNotFoundError):
        backup_service.delete_backup("svr1", backup.name, tmp_path)


def test_delete_backup_traversal_blocked(server, tmp_path):
    backup_service.create_backup("svr1", tmp_path)
    with pytest.raises(BackupNotFoundError):
        backup_service.delete_backup("svr1", "../../evil.zip", tmp_path)


def test_find_backups_none(server, tmp_path):
    with pytest.raises(BackupNotFoundError):
        backup_service.find_backups("svr1", tmp_path)
