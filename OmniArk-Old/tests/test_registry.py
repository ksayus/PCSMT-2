"""服务器注册表与数据模型测试（数据兼容性）。"""

import json

import pytest

from omniark.exceptions import ServerNotFoundError
from omniark.models.server import ServerInstance
from omniark.services import registry


@pytest.fixture()
def workspace(tmp_path):
    (tmp_path / "saves").mkdir()
    return tmp_path


class TestServerInstance:
    def test_round_trip(self, workspace):
        server = ServerInstance(
            Name="test", Counts=1,
            Core=str(workspace / "servers/test/official-server.jar"),
            Path=str(workspace / "servers/test"),
            StartBatchPath=str(workspace / "servers/test/start.bat"),
            Size="54.89MB", Version="1.21.8",
            LatestStartedTime="2025/07/21/16:30:34", CoreType="official",
        )
        server.save(workspace)
        loaded = ServerInstance.load("test", workspace)
        assert loaded == server

    def test_load_missing_raises(self, workspace):
        with pytest.raises(ServerNotFoundError):
            ServerInstance.load("nope", workspace)

    def test_from_dict_ignores_unknown_keys(self):
        server = ServerInstance.from_dict({"Name": "a", "Extra": 1})
        assert server.Name == "a"
        assert server.Counts == 0

    def test_legacy_json_format(self, workspace):
        """旧版 saves/*.json 原样可读。"""
        legacy = {
            "Name": "sr", "Counts": 13,
            "Core": "I:\\servers\\sr\\1.20.1-fabric.jar",
            "Path": "I:\\servers\\sr",
            "StartBatchPath": "I:\\servers\\sr\\start.bat",
            "Size": "54.89MB", "Version": "1.20.1",
            "LatestStartedTime": "2025/10/07/01:27:44",
            "CoreType": "fabric",
        }
        (workspace / "saves/sr.json").write_text(
            json.dumps(legacy, indent=4), encoding="utf-8")
        server = registry.load_server("sr", workspace)
        assert server.CoreType == "fabric"
        assert server.Counts == 13


class TestRegistry:
    def test_list_server_names(self, workspace):
        for name in ("a", "b"):
            ServerInstance(Name=name).save(workspace)
        assert registry.list_server_names(workspace) == ["a", "b"]

    def test_list_skips_empty_and_corrupt(self, workspace):
        ServerInstance(Name="good").save(workspace)
        (workspace / "saves/empty.json").write_text("", encoding="utf-8")
        (workspace / "saves/bad.json").write_text("{oops", encoding="utf-8")
        assert registry.list_server_names(workspace) == ["good"]

    def test_repair_legacy_keys(self, workspace):
        """旧键名（server_name/server_core...）自动迁移。"""
        legacy = {"server_name": "old", "start_count": 5,
                  "server_path": "C:\\nowhere",
                  "server_version": "1.16.5"}
        (workspace / "saves/old.json").write_text(
            json.dumps(legacy), encoding="utf-8")
        server = registry.repair_server_info("old", workspace)
        assert server.Name == "old"
        assert server.Counts == 5
        assert server.Version == "1.16.5"
        # 写回后新键存在
        data = json.loads(
            (workspace / "saves/old.json").read_text(encoding="utf-8"))
        assert "Name" in data and "Core" in data

    def test_remove_server_record(self, workspace):
        ServerInstance(Name="x").save(workspace)
        registry.remove_server_record("x", workspace)
        assert not registry.server_exists("x", workspace)
