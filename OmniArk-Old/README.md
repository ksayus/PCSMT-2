# OmniArk-Old

> Minecraft 服务器管理终端 —— PCSMT-2 的彻底重构版。

## 与旧版（PCSMT-2）的关系

本项目是 PCSMT-2 的架构重构产物，**功能保持一致**，代码完全重写：

| 旧版问题 | 重构方案 |
|---|---|
| 嵌套静态类邪教（`Server.Do.Ban.Player(...)`） | 分层架构：core → models → services → interfaces |
| 模块导入即联网/扫描磁盘 | 显式初始化（`bootstrap.run_bootstrap()`），零导入副作用 |
| 13 处 `os.system` 命令注入风险 | 全部改为 `subprocess` 参数列表 / `requests` |
| 30+ 处 `except Exception: return False` | 具体异常体系（`OmniArkError` 族），接口层统一捕获 |
| 字符串拼接路径、`\` `/` 混用 | 全面 `pathlib.Path`，路径常量在 `core/paths.py` 集中管理 |
| 硬编码 RCON 密码 / Flask secret_key | 配置化 + 随机生成持久化 |
| RCON 等待死循环、定时线程无限叠加 | 超时控制 + 注册表式调度器 |
| 启动/停止依赖 cmd 窗口标题匹配 | subprocess 进程管理（句柄 + PID 文件，进程树结束） |
| Java 版本规则滞后导致 UnsupportedClassVersionError | 启动前实测 jar 内 class 文件版本，自动纠正 Java 选择 |
| 单一管理员账户、无登录保持 | 多账号 + 权限分级（Ksayus 超管/新建默认普通用户）+ 7 天登录会话 |
| 启动服务器弹终端窗口 | 无窗口子进程（CREATE_NO_WINDOW），输出进 logs/console.log |
| 回档无兜底、丢档风险 | 回档前自动备份当前存档（pre-restore）+ 手动原生备份 |
| 文件管理 API 无鉴权 | 浏览需登录、写操作需管理员（superuser_required） |
| 测试覆盖率 < 5% | pytest 单元测试（73 项：配置/注册表/properties/进程/Java/账号/备份/Web 冒烟） |

## 架构

```
omniark/
├── core/          # 基础设施：路径、配置、日志、引导
├── models/        # 数据模型（ServerInstance，兼容旧版 saves/*.json）
├── services/      # 业务层（无 UI 依赖）
│   ├── server_service.py      # 服务器生命周期
│   ├── player_service.py      # 玩家管理（RCON）
│   ├── registry.py            # 注册表（saves/*.json CRUD）
│   ├── properties.py          # server.properties 精确读写
│   ├── backup_service.py      # 回档（FTB Backups 2 / eBackup）
│   ├── core_downloader.py     # 核心下载（official/forge/fabric/mohist）
│   ├── java_service.py        # Java 检测/jar class 版本实测/自动纠正/安装
│   ├── process_manager.py     # 服务器进程管理（subprocess + PID 持久化）
│   ├── rcon_service.py        # RCON 远程控制
│   ├── storage_service.py     # 存储统计 + Excel 报表
│   ├── update_service.py      # GitHub/Gitee 双源自更新
│   ├── security_service.py    # RSA 密钥 + 管理员账户
│   ├── system_service.py      # 开机自启/快捷方式/进程
│   ├── file_manager_service.py# 服务器文件管理（含防穿越）
│   └── program_service.py     # 程序级配置/清理/资源监控
├── interfaces/    # 三套界面，共享 services 层
│   ├── cli/       # cmd2 命令行（34 个命令，与旧版同名）
│   ├── web/       # Flask + 蓝图（API + 现代化深色 SPA）
│   └── gui/       # pywebview 桌面窗口（内嵌 Web 界面，功能与 Web 完全一致）
└── utils/         # 文件/格式化/时间/进程工具
```

## 安装与运行

```bash
pip install -r requirements.txt
python main.py          # 默认 GUI（原生窗口承载 Web 界面，需 Edge WebView2）
python main.py --cli    # 命令行（同时后台启动 Web 服务）
python main.py --web    # 仅 Web 界面（浏览器访问）
```

> GUI 基于 pywebview：Flask 在后台线程提供 Web 界面，原生窗口内嵌显示。
> 因此桌面端与浏览器端功能完全一致；pywebview 不可用时自动回退为浏览器打开。

## 数据兼容

直接读取旧版数据，无需迁移：

- `config.json` —— 11 个配置键完全兼容
- `saves/<名>.json` —— 九字段兼容，旧键名（`server_name` 等）自动迁移
- `server_storage_size/<名>.json` —— 存储历史平行数组
- `servers/` —— 服务器实例目录原样可用
- `C:\PCSMT2-key\` —— RSA 密钥与管理员账户

## 测试

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```

## 文档

- `docs/spec-command.md` —— 旧版 command 层行为规格（重构基线）
- `docs/spec-api-download.md` —— 旧版 Web/下载层行为规格
- `docs/spec-console-gui.md` —— 旧版 CLI/GUI 行为规格

## 许可

沿用原项目约定：可自由修改/发布/集成，保留作者与版权声明即可。
原作者：Ksayus（PCSMT-2）。
