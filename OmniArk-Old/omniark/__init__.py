"""OmniArk-Old —— Minecraft 服务器管理终端（PCSMT-2 重构版）。

分层架构：
    core        路径、配置、日志等基础设施
    models      数据模型（与旧版 saves/*.json 兼容）
    services    业务逻辑层（无 UI 依赖）
    interfaces  CLI / Web / GUI 三套用户界面
    utils       通用工具函数
"""

__version__ = "1.2.2.1.3"
__release_channel__ = "Release"
PROGRAM_NAME = "OmniArk-Old"
LEGACY_PROGRAM_NAME = "PCSMT2"
