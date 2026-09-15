"""密钥与管理员账户服务（替代旧版 Key.py + Admin.py）。

密钥与账户文件保持旧版位置与格式（C:\\PCSMT2-key\\），保证数据兼容。

修复的旧版 bug：
- Load.Key 重新生成密钥后返回 None 导致 TypeError
- AdminAccount 成功路径无返回值
- 重新生成密钥时不覆盖已有密钥（避免旧密文失效）
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from omniark.core.logger import get_logger
from omniark.exceptions import OmniArkError

logger = get_logger()

# 与旧版一致的密钥/账户根目录（Windows 本地使用，保持兼容）
KEY_ROOT = Path(r"C:\PCSMT2-key")
PRIVATE_KEY_FILE = "private.pem"
PUBLIC_KEY_FILE = "public.pem"
ACCOUNT_DIR = "account"


class SecurityError(OmniArkError):
    """密钥或账户操作失败。"""


# ------------------------------------------------------------ RSA 密钥

def generate_key_pair(overwrite: bool = False) -> None:
    """生成 RSA-2048 密钥对。默认不覆盖已有密钥（避免旧密文失效）。"""
    KEY_ROOT.mkdir(parents=True, exist_ok=True)
    private_path = KEY_ROOT / PRIVATE_KEY_FILE
    public_path = KEY_ROOT / PUBLIC_KEY_FILE
    if not overwrite and private_path.exists() and public_path.exists():
        logger.debug("密钥对已存在，跳过生成")
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    public_path.write_bytes(private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    logger.info("RSA 密钥对已生成: %s", KEY_ROOT)


def ensure_key_pair() -> None:
    """确保密钥对存在（任一缺失则补齐；私钥丢失时只能整体重建）。"""
    private_path = KEY_ROOT / PRIVATE_KEY_FILE
    public_path = KEY_ROOT / PUBLIC_KEY_FILE
    if private_path.exists() and public_path.exists():
        return
    if private_path.exists() != public_path.exists():
        logger.warning("密钥对不完整，重新生成（旧密文将不可解密）")
    generate_key_pair(overwrite=True)


def _load_private_key():
    ensure_key_pair()
    return serialization.load_pem_private_key(
        (KEY_ROOT / PRIVATE_KEY_FILE).read_bytes(), password=None)


def _load_public_key():
    ensure_key_pair()
    return serialization.load_pem_public_key(
        (KEY_ROOT / PUBLIC_KEY_FILE).read_bytes())


def encrypt(text: str) -> bytes:
    """公钥加密（OAEP + MGF1/SHA256，与旧版一致）。"""
    return _load_public_key().encrypt(
        text.encode("utf-8"),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None),
    )


def decrypt(cipher_text: bytes) -> str:
    """私钥解密。失败抛 SecurityError。"""
    try:
        return _load_private_key().decrypt(
            cipher_text,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                         algorithm=hashes.SHA256(), label=None),
        ).decode("utf-8")
    except Exception as exc:
        raise SecurityError("解密失败（密钥可能已更换）") from exc


# ------------------------------------------------------------ 管理员账户（含权限级别）

# 超级管理员：始终为 admin，不可降级、不可删除
SUPER_ADMIN = "Ksayus"
ROLES = ("admin", "user")
DEFAULT_ROLE = "user"  # 新建账户默认普通用户


def _account_dir() -> Path:
    return KEY_ROOT / ACCOUNT_DIR


def _account_file(account: str) -> Path:
    # 账户名只取文件名部分，防目录穿越
    safe_name = Path(account).name
    return _account_dir() / f"{safe_name}.bin"


def _read_account(file: Path) -> tuple[bytes, str]:
    """读取账户文件，返回 (加密密码, 角色)。

    兼容两种格式：
    - 新版 JSON：{"password": <base64 RSA 密文>, "role": "admin"|"user"}
    - 旧版裸密文：整个文件即 RSA 密文，角色按 admin 处理（旧版只有管理员）
    """
    raw = file.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
        password = base64.b64decode(data["password"])
        role = data.get("role", DEFAULT_ROLE)
        if role not in ROLES:
            role = DEFAULT_ROLE
        return password, role
    except (ValueError, KeyError, UnicodeDecodeError):
        return raw, "admin"  # 旧版格式：原本就是管理员账户


def _write_account(file: Path, password_cipher: bytes, role: str) -> None:
    data = {"password": base64.b64encode(password_cipher).decode("ascii"),
            "role": role}
    file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def admin_account_exists(account: str | None = None) -> bool:
    """检查管理员账户是否存在。

    account=None 时检查是否存在任意一个有效账户文件。
    """
    directory = _account_dir()
    if account is None:
        if not directory.is_dir():
            return False
        return any(p.is_file() and p.stat().st_size > 0
                   for p in directory.glob("*.bin"))
    file = _account_file(account)
    return file.is_file() and file.stat().st_size > 0


def create_admin_account(account: str, password: str,
                         role: str = DEFAULT_ROLE) -> None:
    """创建账户（密码 RSA 加密存储）。已存在抛 SecurityError。

    默认普通用户；Ksayus 强制为管理员。
    """
    account = account.strip()
    if not account:
        raise SecurityError("账户名不能为空")
    if admin_account_exists(account):
        raise SecurityError(f"账户已存在: {account}")
    if role not in ROLES:
        raise SecurityError(f"无效的权限级别: {role}")
    if account.lower() == SUPER_ADMIN.lower():
        role = "admin"
    _account_dir().mkdir(parents=True, exist_ok=True)
    _write_account(_account_file(account), encrypt(password), role)
    logger.info("账户已创建: %s（%s）", account, role)


def verify_admin_password(account: str, password: str) -> bool:
    """校验账户密码。账户不存在或解密失败均返回 False。"""
    file = _account_file(account)
    if not file.is_file():
        return False
    try:
        cipher, _role = _read_account(file)
        return decrypt(cipher) == password
    except SecurityError:
        return False


def get_role(account: str) -> str:
    """获取账户权限级别（'admin'/'user'）。Ksayus 恒为 admin。"""
    if account.lower() == SUPER_ADMIN.lower():
        return "admin"
    file = _account_file(account)
    if not file.is_file():
        return DEFAULT_ROLE
    _cipher, role = _read_account(file)
    return role


def set_role(account: str, role: str) -> None:
    """修改账户权限级别。Ksayus 不可降级。"""
    if role not in ROLES:
        raise SecurityError(f"无效的权限级别: {role}")
    if account.lower() == SUPER_ADMIN.lower():
        raise SecurityError(f"{SUPER_ADMIN} 是超级管理员，不可修改权限")
    file = _account_file(account)
    if not file.is_file():
        raise SecurityError(f"账户不存在: {account}")
    cipher, _old = _read_account(file)
    _write_account(file, cipher, role)
    logger.info("账户 %s 权限已修改为 %s", account, role)


def list_admin_accounts() -> list[str]:
    """列出全部账户名（按名称排序）。"""
    directory = _account_dir()
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob("*.bin")
                  if p.is_file() and p.stat().st_size > 0)


def list_accounts_with_roles() -> list[dict[str, str]]:
    """列出全部账户及其权限级别。"""
    return [{"account": name, "role": get_role(name)}
            for name in list_admin_accounts()]


def delete_admin_account(account: str) -> None:
    """删除账户。不允许删除最后一个账户或超级管理员。"""
    if account.lower() == SUPER_ADMIN.lower():
        raise SecurityError(f"{SUPER_ADMIN} 是超级管理员，不可删除")
    accounts = list_admin_accounts()
    if account not in accounts:
        raise SecurityError(f"账户不存在: {account}")
    if len(accounts) <= 1:
        raise SecurityError("不能删除最后一个账户")
    _account_file(account).unlink()
    logger.info("账户已删除: %s", account)


def change_admin_password(account: str, old_password: str,
                          new_password: str) -> None:
    """修改账户密码（需验证旧密码）。"""
    if not verify_admin_password(account, old_password):
        raise SecurityError("旧密码错误或账户不存在")
    if not new_password.strip():
        raise SecurityError("新密码不能为空")
    file = _account_file(account)
    cipher, role = _read_account(file)
    _write_account(file, encrypt(new_password), role)
    logger.info("账户 %s 密码已修改", account)
