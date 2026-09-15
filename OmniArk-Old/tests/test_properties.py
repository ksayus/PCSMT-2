"""server.properties 读写测试（验证旧版子串匹配 bug 已修复）。"""

from omniark.services import properties


SAMPLE = """\
#Minecraft server properties
server-port=25565
gamemode=survival
spawn-protection=16
spawn-npcs=true
online-mode=true
motd=A Minecraft Server
"""


class TestReadProperties:
    def test_read(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text(SAMPLE, encoding="utf-8")
        props = properties.read_properties(f)
        assert props["server-port"] == "25565"
        assert props["gamemode"] == "survival"
        assert props["motd"] == "A Minecraft Server"

    def test_missing_file_returns_empty(self, tmp_path):
        assert properties.read_properties(tmp_path / "nope") == {}

    def test_value_containing_equals(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text("motd=a=b=c\n", encoding="utf-8")
        assert properties.get_value(f, "motd") == "a=b=c"


class TestSetValue:
    def test_exact_key_match(self, tmp_path):
        """修改 spawn-protection 不得误伤 spawn-npcs（旧版子串匹配 bug）。"""
        f = tmp_path / "server.properties"
        f.write_text(SAMPLE, encoding="utf-8")
        properties.set_value(f, "spawn-protection", "0")
        props = properties.read_properties(f)
        assert props["spawn-protection"] == "0"
        assert props["spawn-npcs"] == "true"

    def test_preserves_comments_and_other_lines(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text(SAMPLE, encoding="utf-8")
        properties.set_value(f, "gamemode", "creative")
        text = f.read_text(encoding="utf-8")
        assert "#Minecraft server properties" in text
        assert "server-port=25565" in text
        assert "gamemode=creative" in text

    def test_append_new_key(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text(SAMPLE, encoding="utf-8")
        properties.set_value(f, "rcon.port", "25575")
        assert properties.get_value(f, "rcon.port") == "25575"

    def test_set_values_batch(self, tmp_path):
        f = tmp_path / "server.properties"
        f.write_text(SAMPLE, encoding="utf-8")
        properties.set_values(f, {"gamemode": "creative",
                                  "difficulty": "hard",
                                  "max-players": "20"})
        props = properties.read_properties(f)
        assert props["gamemode"] == "creative"
        assert props["difficulty"] == "hard"
        assert props["max-players"] == "20"
