"""Java 管理器：jar class 版本检测与自动纠正测试。"""

import io
import struct
import zipfile

import pytest

from omniark.services import java_service


def _make_class_bytes(major: int) -> bytes:
    """构造一个最小合法 class 文件头（magic + minor + major）。"""
    return b"\xca\xfe\xba\xbe" + struct.pack(">HH", 0, major) + b"\x00" * 8


def _make_fake_jar(path, classes: dict[str, int]) -> None:
    """写入一个假 jar：每个条目是带指定主版本号的 class 头。"""
    with zipfile.ZipFile(path, "w") as zf:
        for name, major in classes.items():
            zf.writestr(name, _make_class_bytes(major))
        zf.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\n")


def test_jar_required_java_major(tmp_path):
    jar = tmp_path / "server.jar"
    _make_fake_jar(jar, {"A.class": 52, "B.class": 65, "C.class": 61})
    # 最高 65 -> Java 21
    assert java_service.jar_required_java_major(jar) == 21


def test_jar_required_java_major_new_version(tmp_path):
    """复现用户报错场景：class 69.0 -> 需要 Java 25。"""
    jar = tmp_path / "new-server.jar"
    _make_fake_jar(jar, {"net/minecraft/bundler/Main.class": 69})
    assert java_service.jar_required_java_major(jar) == 25


def test_jar_required_java_major_invalid(tmp_path):
    assert java_service.jar_required_java_major(tmp_path / "missing.jar") is None
    bad = tmp_path / "bad.jar"
    bad.write_bytes(b"not a zip")
    assert java_service.jar_required_java_major(bad) is None


def test_required_java_for_server_prefers_jar(tmp_path):
    jar = tmp_path / "core.jar"
    _make_fake_jar(jar, {"Main.class": 69})  # 需要 Java 25
    required, source = java_service.required_java_for_server(jar, "1.20.5")
    assert required == "25"  # MC 规则说 21，jar 实测 25 -> 取较大值
    assert "jar" in source


def test_required_java_for_server_rule_fallback(tmp_path):
    jar = tmp_path / "core.jar"
    _make_fake_jar(jar, {"Main.class": 52})  # Java 8
    required, _ = java_service.required_java_for_server(jar, "1.20.5")
    assert required == "21"  # jar 较旧时以 MC 规则为准


def test_java_major_parsing():
    assert java_service._java_major("1.8.0_452") == 8
    assert java_service._java_major("17.0.7") == 17
    assert java_service._java_major("21.0.3") == 21
    assert java_service._java_major("") == 0


def test_load_java_versions_preserves_extra_keys(tmp_path):
    mapping = {"1.8": "", "17": r"C:\jdk17\bin\java.exe",
               "25": r"C:\jdk25\bin\java.exe"}
    java_service.save_java_versions(mapping, tmp_path)
    loaded = java_service.load_java_versions(tmp_path)
    assert loaded["25"] == r"C:\jdk25\bin\java.exe"
    assert "21" in loaded  # 默认键补齐


def test_resolve_java_auto_correct(tmp_path, monkeypatch):
    """配置的 Java 版本不符时自动纠正为扫描到的合适版本。"""
    jar = tmp_path / "core.jar"
    _make_fake_jar(jar, {"Main.class": 69})  # 需要 25
    java_service.save_java_versions(
        {"1.8": "", "16": "", "17": "", "21": r"C:\old\java.exe", "25": ""},
        tmp_path)

    monkeypatch.setattr(java_service, "java_version",
                        lambda p: {"C:/jdk25/bin/java.exe": "25.0.1",
                                   r"C:\old\java.exe": "21.0.3"}.get(
                            str(p).replace("\\", "/"), "21.0.3"))
    monkeypatch.setattr(java_service, "find_java_installations",
                        lambda: [])
    monkeypatch.setattr(
        java_service, "find_matching_java",
        lambda target, extra_paths=None, exact=False:
        {"C:/jdk25/bin/java.exe": "25.0.1"} if target == "25" else {})

    # 配置的 21 不存在（is_file False）→ 扫描命中 25
    java_path, source = java_service.resolve_java_for_server(
        jar, "1.21", tmp_path)
    assert java_path == "C:/jdk25/bin/java.exe"
    assert "jar" in source
