"""Web 层快速冒烟测试（不依赖网络、不依赖真实 Minecraft 服务器）。

pytest 风格：推荐 ``pytest tests/test_web_smoke.py`` 运行；
在没有 pytest 的环境中也可以直接 ``python tests/test_web_smoke.py``。

通过 ``OMNIARK_HOME`` 把配置 / 密钥 / 数据目录全部隔离到临时目录，
不会污染真实工作目录。
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# 必须在导入 omniark 之前设置：所有路径（配置、.secret_key、saves 等）
# 都基于 OMNIARK_HOME 惰性解析。隔离目录放在项目内（.smoke-home），
# 避免对系统临时目录的写权限依赖。
_SMOKE_HOME = Path(__file__).resolve().parents[1] / ".smoke-home"
# 每次运行前清空，保证测试间状态可预期
shutil.rmtree(_SMOKE_HOME, ignore_errors=True)
_SMOKE_HOME.mkdir(exist_ok=True)
os.environ["OMNIARK_HOME"] = str(_SMOKE_HOME)

# 允许从项目根目录外直接运行本文件
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from omniark.interfaces.web.app import create_app  # noqa: E402


def _client():
    app = create_app()
    app.testing = True
    return app.test_client()


# ------------------------------------------------------------ 测试用例

def test_app_factory_registers_routes() -> None:
    """应用工厂可用，且注册了大量路由。"""
    app = create_app()
    rules = list(app.url_map.iter_rules())
    assert len(rules) > 20, f"路由数量异常: {len(rules)}"


def test_api_index() -> None:
    resp = _client().get("/api")
    assert resp.status_code == 200
    assert "PCSMT2" in resp.get_data(as_text=True)


def test_program_version() -> None:
    resp = _client().get("/api/program/version")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data is not None and "version" in data


def test_server_list_empty() -> None:
    """空工作目录下服务器列表为空，serverCount 是数量（修复旧版 bug）。"""
    resp = _client().get("/api/server/list")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["serverlist"] == []
    assert data["serverCount"] == 0


def test_program_get_settings() -> None:
    resp = _client().get("/api/program/get/settings")
    assert resp.status_code == 200
    data = resp.get_json()
    for key in ("min_memory", "max_memory", "nogui_enabled",
                    "eula_wait_time", "auto_start", "update_source",
                    "test_versions", "storage_update_time", "server_port"):
        assert key in data, f"缺少设置项: {key}"


def test_server_info_not_found() -> None:
    """不存在的服务器 → 404 + 统一错误格式。"""
    resp = _client().get("/api/server/info/不存在的服务器")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False and "error" in data


def test_latest_not_found() -> None:
    """latest.json 不存在时返回 404 JSON（修复旧版 return False）。"""
    resp = _client().get("/api/server/latest")
    assert resp.status_code == 404
    assert resp.get_json()["success"] is False


def test_protected_route_requires_login() -> None:
    """start/stop/delete/command 未登录时 AJAX 请求 → 401。"""
    client = _client()
    for url in ("/api/server/xxx/start", "/api/server/xxx/stop",
                "/api/server/delete/xxx", "/api/server/xxx/command"):
        resp = client.post(url, headers={"X-Requested-With": "XMLHttpRequest"},
                           json={"command": "list"})
        assert resp.status_code == 401, f"{url} 未鉴权: {resp.status_code}"
        assert resp.get_json()["success"] is False


def test_static_ico() -> None:
    resp = _client().get("/api/static/ico")
    assert resp.status_code == 200


def test_index_page() -> None:
    """首页默认要求登录：未登录 302 到 /login，登录后 200。"""
    client = _client()
    resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
    # 直接注入已登录会话
    with client.session_transaction() as sess:
        sess["authenticated"] = True
    resp = client.get("/")
    assert resp.status_code == 200


# ------------------------------------------------------------ 伪造服务器（不启动真实进程）

def _fabricate_server(name: str = "testsvr") -> Path:
    """在隔离工作目录里伪造一个已注册服务器（目录 + start.bat +
    server.properties + logs + saves JSON）。"""
    server_dir = _SMOKE_HOME / "servers" / name
    (server_dir / "logs").mkdir(parents=True, exist_ok=True)
    (server_dir / "start.bat").write_text(
        f"cd {server_dir}\njava -Xms512M -Xmx1024M -jar core.jar -nogui\nexit",
        encoding="utf-8")
    (server_dir / "core.jar").write_bytes(b"fake")
    (server_dir / "server.properties").write_text(
        "server-port=25565\nwhite-list=false\ngamemode=survival\n",
        encoding="utf-8")
    (server_dir / "logs" / "latest.log").write_text(
        "[12:00:00] Server started\n[12:00:01] Done\n", encoding="utf-8")
    import json
    save = {
        "Name": name, "Counts": 1, "Core": str(server_dir / "core.jar"),
        "Path": str(server_dir),
        "StartBatchPath": str(server_dir / "start.bat"),
        "Size": "1KB", "Version": "1.20.1",
        "LatestStartedTime": "N/A", "CoreType": "official",
    }
    saves = _SMOKE_HOME / "saves"
    saves.mkdir(exist_ok=True)
    (saves / f"{name}.json").write_text(
        json.dumps(save, ensure_ascii=False), encoding="utf-8")
    return server_dir


def test_fabricated_server_apis() -> None:
    """基于伪造服务器验证查询类 API（无需网络与真实进程）。"""
    server_dir = _fabricate_server()
    client = _client()

    resp = client.get("/api/server/list")
    data = resp.get_json()
    assert "testsvr" in data["serverlist"]
    assert data["serverCount"] == len(data["serverlist"])

    # 状态：未运行也是 200，用 status 字段区分（修复旧版 502 语义滥用）
    resp = client.get("/api/server/status/testsvr")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "stopped" and data["online"] is False

    # 运行内存解析
    resp = client.get("/api/server/get/run_memory/testsvr")
    assert resp.get_json() == {"min": 512, "max": 1024}

    # server.properties 读取
    resp = client.get("/api/server/get/document/server.properties/testsvr")
    data = resp.get_json()
    assert data["server-port"] == "25565" and data["gamemode"] == "survival"

    # 终端日志（修复旧版无返回值 bug）
    resp = client.get("/api/server/get/testsvr/terminal/logs")
    data = resp.get_json()
    assert data["success"] is True
    assert any("Server started" in line for line in data["logs"])

    # 白名单未启用
    resp = client.get("/api/server/get/white-list/testsvr")
    assert resp.get_json()["success"] is False

    # 封禁玩家列表（空）
    resp = client.get("/api/server/get/banned/players/testsvr")
    data = resp.get_json()
    assert data["success"] is True and data["BannedPlayerList"] == []


def test_file_manager_api() -> None:
    """文件管理器 API：list/create/rename/copy/move/delete + 越界防护。"""
    server_dir = _fabricate_server("mgsvr")
    client = _client()
    # 文件管理器需要登录（写操作需 admin 角色）
    with client.session_transaction() as sess:
        sess["authenticated"] = True
        sess["admin_account"] = "testadmin"
        sess["role"] = "admin"
    base = "/api/manager/mgsvr"

    # 目录浏览（绝对路径与相对路径都接受）
    resp = client.get(f"{base}/list")
    data = resp.get_json()
    assert data["success"] is True and data["FilesCounts"] >= 2

    # 新建文件/文件夹
    assert client.post(f"{base}/create/file",
                       json={"path": "notes.txt"}).get_json()["success"]
    assert client.post(f"{base}/create/folder",
                       json={"path": "subdir"}).get_json()["success"]

    # 重命名（前端传完整新路径，后端只取文件名）
    assert client.post(f"{base}/rename", json={
        "old_path": "notes.txt",
        "new_path": "notes_renamed.txt"}).get_json()["success"]

    # 复制 / 移动
    assert client.post(f"{base}/copy", json={
        "source_paths": ["notes_renamed.txt"],
        "target_path": "subdir"}).get_json()["success"]
    assert client.post(f"{base}/move", json={
        "source_paths": ["notes_renamed.txt"],
        "target_path": "subdir"}).get_json()["success"]

    # 删除
    assert client.post(f"{base}/delete/file",
                       json={"path": "subdir/notes_renamed.txt"}
                       ).get_json()["success"]
    assert client.post(f"{base}/delete/folder",
                       json={"path": "subdir"}).get_json()["success"]

    # 越界路径必须被拒绝（400，统一错误格式）
    resp = client.post(f"{base}/delete/file",
                       json={"path": "../../outside.txt"})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False

    # 旧版 /api/get/directory：服务器目录内可读，目录外 404
    resp = client.get(f"/api/get/directory?path={server_dir}")
    assert resp.status_code == 200
    assert "CurrentDirectory" in resp.get_json()
    resp = client.get("/api/get/directory?path=C:/Windows")
    assert resp.status_code == 404


# ------------------------------------------------------------ 无 pytest 时的简易运行器

if __name__ == "__main__":
    failed = 0
    # 按定义顺序执行（测试间共享隔离工作目录，顺序有意义）
    tests = [(name, func) for name, func in globals().items()
             if name.startswith("test_") and callable(func)]
    for name, func in tests:
        try:
            func()
            print(f"PASS {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} 通过")
    sys.exit(1 if failed else 0)
