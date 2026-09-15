"""OmniArk-Old 程序入口。

用法：
    python main.py            # 默认启动 Tkinter GUI（与旧版一致）
    python main.py --cli      # 命令行终端
    python main.py --gui      # Tkinter 桌面界面
    python main.py --web      # 仅启动 Web 管理界面（前台）
    python main.py --cli --no-bootstrap   # 跳过初始化（调试用）
"""

from __future__ import annotations

import argparse
import sys


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="OmniArk-Old",
        description="Minecraft 服务器管理终端（PCSMT-2 重构版）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--cli", action="store_true", help="命令行终端")
    mode.add_argument("--gui", action="store_true", help="Tkinter 桌面界面（默认）")
    mode.add_argument("--web", action="store_true", help="仅启动 Web 管理界面")
    parser.add_argument("--no-bootstrap", action="store_true",
                        help="跳过初始化引导")
    parser.add_argument("--no-web", action="store_true",
                        help="不随 CLI/GUI 启动后台 Web 服务")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # 初始化引导
    if not args.no_bootstrap:
        from omniark.core.bootstrap import run_bootstrap
        # 仅 CLI 模式允许交互式创建管理员账户（GUI/Web 模式无控制台会卡死）
        run_bootstrap(interactive=args.cli)

    # Web 后台服务只在 CLI 模式启动；GUI 模式由 OmniArkApp 自己内嵌 Web 服务
    if args.cli and not args.no_web:
        import threading
        from omniark.interfaces.web.app import run as run_web
        threading.Thread(target=run_web, daemon=True).start()

    if args.web:
        from omniark.interfaces.web.app import run as run_web
        run_web()  # 前台阻塞
        return 0

    if args.cli:
        # 进入软件默认要求登录（已有账户时）
        if not _cli_login():
            return 1
        from omniark.interfaces.cli.shell import OmniArkShell
        try:
            OmniArkShell().cmdloop()
        except KeyboardInterrupt:
            print("\n退出 OmniArk，正在安全关闭...")
        return 0

    # 默认 GUI（pywebview 原生窗口承载 Web 界面，功能与 Web 完全一致）
    from omniark.interfaces.gui.app import OmniArkApp
    OmniArkApp().run()
    return 0


def _cli_login(max_attempts: int = 3) -> bool:
    """CLI 启动登录：存在管理员账户时要求验证，3 次机会。

    尚无账户时跳过（bootstrap 已在交互模式引导创建）。
    """
    from omniark.services import security_service
    if not security_service.admin_account_exists():
        return True
    import getpass
    for attempt in range(max_attempts):
        account = input("管理员账号: ").strip()
        password = getpass.getpass("密码: ")
        if security_service.verify_admin_password(account, password):
            print(f"欢迎回来，{account}")
            return True
        remaining = max_attempts - attempt - 1
        print(f"账号或密码错误（剩余 {remaining} 次机会）")
    print("登录失败次数过多，退出")
    return False


if __name__ == "__main__":
    sys.exit(main())
