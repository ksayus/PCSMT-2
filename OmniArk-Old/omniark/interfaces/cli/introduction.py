"""程序介绍信息（替代旧版 ``bin/introduction/introduction.py``）。

旧版直接读取全局 ``Info.Config``，这里改为从 :mod:`omniark` 元数据与
:func:`omniark.core.config.get_config` 显式获取版本号。
"""

from __future__ import annotations

from omniark import PROGRAM_NAME, __release_channel__, __version__

PROGRAM_FULL_NAME = "PCSMT (Plain Craft Server Management Terminal)"
POWER_BY = "Power by Ksayus"
GITHUB_PAGE = "--Github:\t\thttps://github.com/Ksayus/PCSMT-2"
GITEE_PAGE = "--Gitee:\t\thttps://gitee.com/Ksayus/PCSMT-2"
KSAYUS_PAGE = "--Ksayus:\t\thttps://ksayus.github.io/2025/01/30/PCSMT-2/"
AUTHOR_BILIBILI_PAGE = "--Bilibili:\t\thttps://space.bilibili.com/558271819"
PERSONAL_WEBSITE = "--Personal Website:\thttps://ksayus.github.io"

ASCII_BANNER = r"""-------------------------------
_____   _____  _____ __  __ _______
|  __\ / ____|/  ___|  \/  |__   __|
| |__ )| |    | (___| \  / |  | |
| ___/ | |    \___ \| |\/| |  | |
| |    | |________) | |  | |  | |
|_|    \_____|_____/|_|  |_|  |_|
-------------------------------"""


def version_text() -> str:
    """返回版本号文本，如 ``Version: 1.2.2.1.3-Release``。"""
    return f"Version: {__version__}-{__release_channel__}"


def print_version() -> None:
    """打印版本号（对应旧版 ``introduction.Version``）。"""
    print("-------------------------------")
    print(version_text())
    print("-------------------------------")


def print_homepage() -> None:
    """打印程序介绍主页（对应旧版 ``introduction.Homepage``）。"""
    print(ASCII_BANNER)
    print(f"Welcome {PROGRAM_FULL_NAME}")
    print(f"重构版: {PROGRAM_NAME}")
    print(POWER_BY)
    print("My own homepage-->")
    print(GITHUB_PAGE)
    print(GITEE_PAGE)
    print(KSAYUS_PAGE)
    print(AUTHOR_BILIBILI_PAGE)
    print(PERSONAL_WEBSITE)
    print()
    print(version_text())
    print("-------------------------------")
