"""OmniArk 桌面 GUI（pywebview 实现，替代旧版 Tkinter 壳）。

架构：Flask Web 服务（后台线程）+ 系统原生 WebView2 窗口承载同一套
Web 界面。因此 GUI 的功能与 Web 管理界面**完全一致**，不存在两套实现
的维护与行为漂移问题。

- Windows 上使用系统自带的 Edge WebView2 渲染（Win10/11 默认可用）
- pywebview 缺失或窗口创建失败时自动回退为打开系统浏览器
- 端口被占用时自动选择空闲端口
"""

from __future__ import annotations

import socket
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

from omniark import PROGRAM_NAME, __release_channel__, __version__
from omniark.core.config import get_config
from omniark.core.logger import get_logger

logger = get_logger()


class OmniArkApp:
    """OmniArk 桌面窗口。

    :param host: Web 服务监听地址（默认仅本机）。
    :param port: Web 服务端口；None 时读配置，被占用则自动换空闲端口。
    """

    def __init__(self, host: str = "127.0.0.1", port: int | None = None) -> None:
        self.host = host
        self.port = port or get_config().Port
        if not self._port_free(self.port):
            logger.warning("端口 %d 被占用，自动选择空闲端口", self.port)
            self.port = self._find_free_port()
        self.url = f"http://{self.host}:{self.port}"
        self._server_thread: threading.Thread | None = None

    # ------------------------------------------------------------ 端口

    def _port_free(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((self.host, port))
                return True
            except OSError:
                return False

    def _find_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, 0))
            return sock.getsockname()[1]

    # ------------------------------------------------------------ 服务

    def _start_server(self) -> None:
        """后台线程启动 Flask（development server，仅本地监听）。"""
        from omniark.interfaces.web.app import create_app

        app = create_app()

        def _serve() -> None:
            # 关闭 werkzeug 请求日志，保持桌面端安静
            import logging
            logging.getLogger("werkzeug").setLevel(logging.ERROR)
            app.run(host=self.host, port=self.port,
                    debug=False, use_reloader=False)

        self._server_thread = threading.Thread(
            target=_serve, name="omniark-web", daemon=True)
        self._server_thread.start()

    def _wait_until_ready(self, timeout: float = 15.0) -> bool:
        """等待 Web 服务就绪。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{self.url}/api", timeout=1) as resp:
                    if resp.status == 200:
                        return True
            except OSError:
                time.sleep(0.2)
        return False

    # ------------------------------------------------------------ 运行

    def run(self) -> None:
        """启动 Web 服务并打开原生窗口（阻塞直到窗口关闭）。"""
        self._start_server()
        if not self._wait_until_ready():
            logger.error("Web 服务启动超时")
            return
        logger.info("OmniArk 桌面界面: %s", self.url)

        try:
            import webview
        except ImportError:
            logger.warning("未安装 pywebview（pip install pywebview），"
                           "回退为系统浏览器打开")
            webbrowser.open(self.url)
            self._wait_forever()
            return

        try:
            webview.create_window(
                title=f"{PROGRAM_NAME} v{__version__}-{__release_channel__}",
                url=self.url,
                width=1280, height=800,
                min_size=(960, 600),
                text_select=True,
            )
            # 独占的配置目录（不用默认 %APPDATA%\pywebview，避免与其他
            # pywebview 应用共享缓存）；v2：弃用旧 profile（可能残留旧缓存）。
            # 服务端对 HTML/JS/CSS 发 no-store，且静态资源 URL 带
            # 版本号+启动时间戳（每次启动必换新），界面不可能再读到旧缓存；
            # 持久化配置保留 7 天登录会话（不用 private_mode）
            storage = Path.home() / ".omniark" / "webview-profile-v2"
            storage.mkdir(parents=True, exist_ok=True)
            webview.start(storage_path=str(storage))
        except Exception as exc:  # WebView2 缺失等情况
            logger.error("原生窗口创建失败: %s，回退为浏览器打开", exc)
            webbrowser.open(self.url)
            self._wait_forever()

    def _wait_forever(self) -> None:
        """浏览器回退模式下保持进程存活（Ctrl+C 退出）。"""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("退出 OmniArk")


def run_gui(host: str = "127.0.0.1", port: int | None = None) -> None:
    """便捷入口：启动桌面 GUI。"""
    OmniArkApp(host=host, port=port).run()
