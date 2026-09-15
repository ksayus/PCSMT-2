"""AppConfig 单元测试。"""

import json

import pytest

from omniark.core.config import AppConfig
from omniark.exceptions import ConfigError


class TestAppConfig:
    def test_defaults(self):
        cfg = AppConfig()
        assert cfg.RunningMemories_Min == 1024
        assert cfg.RunningMemories_Max == 2048
        assert cfg.Nogui is True
        assert cfg.Port == 5000
        assert cfg.AutoUpdateSource == "Github"

    def test_round_trip(self, tmp_path):
        cfg = AppConfig(Port=40000, RunningMemories_Min=2048)
        file = tmp_path / "config.json"
        cfg.save(file)
        loaded = AppConfig.load(file)
        assert loaded.Port == 40000
        assert loaded.RunningMemories_Min == 2048
        # 未修改的键保持默认
        assert loaded.Nogui is True

    def test_load_missing_file_returns_defaults(self, tmp_path):
        cfg = AppConfig.load(tmp_path / "nonexistent.json")
        assert cfg == AppConfig()

    def test_load_corrupt_file_raises(self, tmp_path):
        file = tmp_path / "config.json"
        file.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(ConfigError):
            AppConfig.load(file)

    def test_unknown_keys_ignored(self):
        cfg = AppConfig.from_dict({"Port": 1234, "UnknownKey": "x"})
        assert cfg.Port == 1234
        assert not hasattr(cfg, "UnknownKey")

    def test_type_coercion(self):
        cfg = AppConfig.from_dict({"Port": "8080", "Nogui": "false"})
        assert cfg.Port == 8080
        assert cfg.Nogui is False

    def test_bad_type_raises(self):
        with pytest.raises(ConfigError):
            AppConfig.from_dict({"Port": "not-a-number"})

    def test_update(self):
        cfg = AppConfig()
        cfg.update(RunningMemories_Min=4096, Nogui=False)
        assert cfg.RunningMemories_Min == 4096
        assert cfg.Nogui is False

    def test_compat_with_legacy_config(self, tmp_path):
        """与旧版 config.json 完全兼容。"""
        legacy = {
            "PCSMT2_Version": "1.2.2.1.3",
            "ReleaseVersion": "Release",
            "RunningMemories_Min": 2048,
            "RunningMemories_Max": 4096,
            "Nogui": True,
            "WaitEulaGenerateTime": 25,
            "AutomaticStartup": False,
            "AutoUpdateSource": "Github",
            "MinecraftTestVersion": False,
            "StorageSizeUpdateTime": 1800,
            "Port": 40000,
        }
        file = tmp_path / "config.json"
        file.write_text(json.dumps(legacy), encoding="utf-8")
        cfg = AppConfig.load(file)
        assert cfg.RunningMemories_Max == 4096
        assert cfg.WaitEulaGenerateTime == 25
        assert cfg.StorageSizeUpdateTime == 1800
