"""process_manager：子进程生命周期管理测试。"""

import sys
import time
from pathlib import Path

import pytest

from omniark.services import process_manager


@pytest.fixture()
def server_dir(tmp_path):
    return tmp_path / "srv"


def _spawn_sleeper(name: str, cwd: Path):
    """启动一个跨平台的常驻子进程（无窗口，输出进 console.log）。"""
    cwd.mkdir(parents=True, exist_ok=True)
    return process_manager.start(
        name, [sys.executable, "-c", "import time; time.sleep(60)"],
        cwd=cwd)


def test_start_registers_pid(server_dir):
    proc = _spawn_sleeper("alpha", server_dir)
    try:
        assert process_manager.is_running("alpha", server_dir)
        assert process_manager.pid_of("alpha", server_dir) == proc.pid
        # PID 文件已持久化
        assert (server_dir / process_manager.PID_FILENAME).is_file()
    finally:
        process_manager.stop("alpha", server_dir)


def test_stop_kills_process_and_cleans_pid(server_dir):
    _spawn_sleeper("beta", server_dir)
    pid = process_manager.pid_of("beta", server_dir)
    assert process_manager.stop("beta", server_dir)
    deadline = time.time() + 5
    while time.time() < deadline and process_manager._pid_alive(pid):
        time.sleep(0.1)
    assert not process_manager._pid_alive(pid)
    assert not (server_dir / process_manager.PID_FILENAME).exists()
    assert not process_manager.is_running("beta", server_dir)


def test_stop_not_running_is_noop(server_dir):
    server_dir.mkdir(parents=True)
    assert process_manager.stop("ghost", server_dir) is True


def test_status_from_pid_file_after_registry_loss(server_dir):
    """模拟程序重启：清空内存注册表后，仍能通过 PID 文件识别进程。"""
    proc = _spawn_sleeper("gamma", server_dir)
    try:
        process_manager._processes.clear()
        assert process_manager.is_running("gamma", server_dir)
        assert process_manager.pid_of("gamma", server_dir) == proc.pid
    finally:
        process_manager.stop("gamma", server_dir)


def test_stale_pid_file_ignored(server_dir):
    """PID 文件中的 PID 已不存在时视为未运行。"""
    server_dir.mkdir(parents=True)
    (server_dir / process_manager.PID_FILENAME).write_text(
        "99999999", encoding="utf-8")
    assert not process_manager.is_running("ghost2", server_dir)
