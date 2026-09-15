"""多账号管理测试（security_service）。"""

import pytest

from omniark.exceptions import OmniArkError
from omniark.services import security_service
from omniark.services.security_service import SecurityError


@pytest.fixture(autouse=True)
def isolated_key_root(tmp_path, monkeypatch):
    """把 KEY_ROOT 重定向到临时目录，避免碰真实的 C:\\PCSMT2-key。"""
    monkeypatch.setattr(security_service, "KEY_ROOT", tmp_path / "key")
    security_service.ensure_key_pair()
    yield


def test_create_and_verify():
    security_service.create_admin_account("admin1", "pass123")
    assert security_service.admin_account_exists("admin1")
    assert security_service.verify_admin_password("admin1", "pass123")
    assert not security_service.verify_admin_password("admin1", "wrong")


def test_duplicate_create_rejected():
    security_service.create_admin_account("admin1", "pass123")
    with pytest.raises(SecurityError):
        security_service.create_admin_account("admin1", "other")


def test_list_accounts_sorted():
    security_service.create_admin_account("b_user", "p1")
    security_service.create_admin_account("a_user", "p2")
    assert security_service.list_admin_accounts() == ["a_user", "b_user"]


def test_delete_account():
    security_service.create_admin_account("u1", "p1")
    security_service.create_admin_account("u2", "p2")
    security_service.delete_admin_account("u1")
    assert security_service.list_admin_accounts() == ["u2"]


def test_delete_last_account_rejected():
    security_service.create_admin_account("only", "p")
    with pytest.raises(SecurityError, match="最后一个"):
        security_service.delete_admin_account("only")


def test_delete_missing_account():
    security_service.create_admin_account("u", "p")
    with pytest.raises(SecurityError):
        security_service.delete_admin_account("ghost")


def test_change_password():
    security_service.create_admin_account("u", "old")
    security_service.change_admin_password("u", "old", "new")
    assert security_service.verify_admin_password("u", "new")
    assert not security_service.verify_admin_password("u", "old")


def test_change_password_wrong_old():
    security_service.create_admin_account("u", "old")
    with pytest.raises(SecurityError):
        security_service.change_admin_password("u", "bad", "new")


def test_account_name_traversal_blocked(tmp_path):
    """账户名中的路径分隔符只取文件名部分（防目录穿越）。"""
    security_service.create_admin_account("../evil", "p")
    # 实际落在 account 目录内
    assert security_service.admin_account_exists("evil")
    assert not (security_service.KEY_ROOT / "evil.bin").exists()
