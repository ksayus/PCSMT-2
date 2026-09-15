# PCSMT-2 行为规格文档（供重构使用）

> 基于以下源码逐一通读：`bin/console/commands.py`（489 行，实际并非 600 行）、`bin/gui/app.py`（354 行）、`bin/bootstrap.py`（138 行）、`bin/find_files/{find_file.py, find_folder.py, tree.py}`、`bin/introduction/introduction.py`、`config.json`、`java_versions.json`、`requirements.txt`、`index.html`。

## 1. CLI 命令完整清单（bin/console/commands.py）

CLI 基于 cmd2 库，类 `PCSMT2(Cmd)`，属性 `intro = "欢迎使用PCSMT2"`、`prompt = "PCSMT2>"`。命令即 `do_*` 方法，Tab 补全即 `complete_*` 方法。后端调用来自模块：`bin.introduction.introduction`、`bin.command.{Start, Server, Program}`、`bin.export.{Info, log, numbers}`。

### 命令表

| # | 命令 | 参数 | 功能 | 后端调用 | help 文本 |
|---|------|------|------|----------|-----------|
| 1 | `version` | 无 | 查看版本号 | `introduction.Version()` | `查看版本号\nCommand: version` |
| 2 | `about` | 无 | 查看介绍（ASCII banner+链接+版本） | `introduction.Homepage()` | `查看介绍\nCommand: about` |
| 3 | `sta` | `<file_path>` | 打开文件或目录 | `Start.Open.File(file_path)` | `打开文件或目录\nCommand: sta <file_path>` |
| 4 | `add_server` | `<server_path> <server_name> <server_version> <CoreType>` | 添加服务器（先 print 四个参数） | `Server.Processing.Add(server_path, server_name, False, server_version, CoreType)` | `添加服务器\nCommand: add_server <server_path> <server_name> <server_version> <CoreType>` |
| 5 | `start_server` | `<server_name>` | 启动服务器 | `Server.Do.Start(server_name)` | `启动服务器\nCommand: start_server <server_name>` |
| 6 | `server_list` | 无 | 查看服务器列表 | `Server.Get.List()` | `查看服务器列表\nCommand: server_list` |
| 7 | `change_server_properties` | `<server_name> <keyword> <argument>` | 修改服务器属性 | `Server.Change.Properties(server_name, keyword, argument)` | `修改服务器属性\nCommand: change_server_properties <server_name> <keyword> <argument>` |
| 8 | `change_server_run_memories_config` | `<memories_min> <memories_max>` | 修改默认运行内存 | isdigit 校验 + min>max 时 `numbers.swap_numbers` 交换后 `Program.Change.RunningMemories_Config(min, max)` | `修改写入服务器启动脚本默认使用运行内存\nCommand: change_server_run_memories_config <memories_min> <memories_max>` |
| 9 | `server_mods` | `<server_name>` | 打开 mods/plugins 文件夹 | `Server.Do.Open.Mods_Plugins_Folders(server_name)` | `查看服务器插件列表\nCommand: server_mods <server_name>` |
| 10 | `server_start_batch_rewrite_run_memories` | `<server_name> <memories_min> <memories_max>` | 重写启动脚本内存 | 同上校验后 `Server.Change.RunningMemories(server_name, min, max)` | `重写服务器启动脚本\nCommand: server_start_batch_rewrite_run_memories <server_name> <memories_min> <memories_max>` |
| 11 | `change_server_start_nogui` | `<true/false>` | 修改 nogui（仅接受小写） | `Program.Change.Nogui(argument)` | `修改服务器启动nogui\nCommand: change_server_start_nogui <true/false>` |
| 12 | `build` | `<server_name> <core_type> <game_version>` | 下载服务器核心 | `Server.Processing.Build(server_name, core_type, core_support_version)` | `下载服务器核心\nCommand: Build <server_name> <core_type> <game_version>` |
| 13 | `change_wait_server_eula_generate_time` | `<time>` | 修改等待 eula 生成时间 | `Program.Change.WaitEulaGenerateTime(argument)` | `修改等待服务器eula生成时间\nCommand: change_wait_server_eula_generate_time <time>` |
| 14 | `delete_server` | `<server_name>` | 删除服务器 | `Server.Processing.Delete(server_name, True)` | `删除服务器\nCommand: delete_server <server_name>` |
| 15 | `search_server` | `<server_name>` | 搜索服务器 | `Server.Get.Search(server_name)` | `搜索服务器\nCommand: search_server <server_name>` |
| 16 | `banned` | `<players/ips> <server_name> <player/ip>` | 封禁玩家或 IP | `Server.Do.Ban.Ip(server_name, ip)` / `Server.Do.Ban.Player(server_name, player)` | `封禁玩家或ip\nCommand: banned <players / ips> <server_name> <player_name / ip>` |
| 17 | `unban` | 同上 | 解封玩家或 IP | `Server.Do.Unban.Ip(...)` / `Server.Do.Unban.Player(...)` | `解封玩家或ip\nCommand: unban <players / ips> <server_name> <player_name / ip>` |
| 18 | `op` | `<server_name> <player_name>` | 添加 OP | `Server.Do.Set.Op(server_name, player_name)` | `添加OP玩家\nCommand: op <server_name> <player_name>` |
| 19 | `deop` | 同上 | 删除 OP | `Server.Do.Set.Deop(...)` | `删除OP玩家\nCommand: deop <server_name> <player_name>` |
| 20 | `stop_server` | `<server_name>` | 停止服务器 | `Server.Do.Stop(server_name)` | `停止服务器\nCommand: stop_server <server_name>` |
| 21 | `change_program_auto_startup` | `<True/False>` | 修改自动启动（无值校验） | `Program.Change.AutoStartup(argument)` | `修改程序自动启动\nCommand: change_program_auto_startup <True / False>` |
| 22 | `rename_server` | `<server_name> <new_name>` | 重命名服务器 | `Server.Change.Rename(server_name, new_name)` | `重命名服务器\nCommand: rename_server <server_name> <new_name>` |
| 23 | `redirected_server_path` | `<server_name> <new_path>` | 重定向服务器路径 | `Server.Change.Redirected(server_name, new_path)` | `重定向服务器路径\nCommand: redirected_server_path <server_name> <new_path>` |
| 24 | `latest_started_server` | 无 | 启动最新服务器 | `Server.Do.StartLatest()` | `启动最新服务器\nCommand: latest_started_server` |
| 25 | `output_program_info` | 无 | 输出程序信息 | `Program.Output.ProgramInfo()` | `输出程序信息\nCommand: out_program_info`（help 与命令名不一致） |
| 26 | `format_program` | 无 | 格式化程序 | `Program.Format.Program()` | `格式化程序\nCommand: format_program` |
| 27 | `clear_cache` | 无 | 清除缓存 | `Program.Format.Log()` + `Program.Format.Latest()` | `清除缓存\nCommand: clear_cache` |
| 28 | `reset_settings` | 无 | 重置设置 | `Program.Format.Settings()` | `重置设置\nCommand: reset_settings` |
| 29 | `change_get_minecraft_test_version` | `<True/False>` | 修改获取测试版版本 | `Program.Change.MinecraftTestVersion(argument)` | `修改获取测试版服务器版本\nCommand: change_get_minecraft_test_version <True / False>` |
| 30 | `retracement` | `[server_name] [backup_file]` | 回档服务器（第二参可选） | 校验服务器名在 ServerList 后 `Server.Processing.Retracement(server_name, backup_file)`（可为 None） | `回档服务器\nCommand: retracement [server_name]` |
| 31 | `change_storage_size_update_time` | `<time>` | 修改存储大小更新时间（**无 docstring**） | isdigit 校验后 `Program.Change.StorageSizeUpdateTime(time)` | 无（help 中无说明） |
| 32 | `change_port` | `<port>` | 修改端口（**无 docstring**） | isdigit 校验后 `Program.Change.Port(int(port))` | 无 |
| 33 | `change_update_source` | `<update_source>` | 修改更新源 | `Program.Change.UpdateSource(argument)` | `修改更新源\nCommand: change_update_source <update_source>` |
| 34 | `exit` | 无 | 退出控制台 | 打印"再见！"+"欢迎再次使用PCSMT 2"后 `sys.exit(0)`（其后 `return True` 不可达） | `退出控制台\nCommand: exit` |

### Tab 补全行为

- `complete_add_server`：arg1=path_complete，arg2=ServerList，arg3=MinecraftVersion。
- `complete_start_server` / `server_mods` / `delete_server` / `search_server` / `op` / `deop` / `stop_server` / `rename_server`：arg1=ServerList。
- `complete_change_server_properties`：arg1=ServerList，arg2=PropertiesKeys，arg3 按 key 给枚举：gamemode→[survival,creative,adventure,spectator]，difficulty→[peaceful,easy,normal,hard]，布尔键（pvp/allow-flight/spawn-protection/spawn-npcs/spawn-animals/spawn-monsters/online-mode）→[true,false]。
- `complete_build`：arg2=[fabric, forge, official, mohist]，arg3=MinecraftVersion。
- `complete_banned`/`complete_unban`：arg1=[ips,players]，arg2=ServerList。
- `complete_redirected_server_path`：arg1=ServerList，arg2=path_complete。
- `complete_retracement`：arg1=ServerList，arg2=`Server.Get.FindBackupFile(arg[0])` 结果 + 'None'。
- `complete_change_update_source`：[github, gitee]。
- `complete_change_server_start_nogui` / `change_program_auto_startup` / `change_get_minecraft_test_version`：[true, false]。
- `complete_help` 被重写：补全所有命令名（`self.get_all_commands()` 前缀过滤）。
- 所有补全按 `startswith(text)` 前缀过滤；变量名普遍用 `list`/`type` 遮蔽内建。

### 通用模式

- 多参命令用 `arg.split()` 捕 ValueError，参数数量错误时 `log.logger.error('参数错误，请输入正确的参数！')` 并 return。
- 单参命令普遍写成 `try: arg.strip() except ValueError`——**strip 不抛 ValueError，该 except 永不触发**（见 bug 列表）。

## 2. GUI 结构与行为（bin/gui/app.py，Tkinter）

类 `TkinterApp`，构造时接收一个 cmd2 实例 `cmd_instance`（即 PCSMT2 CLI 实例，GUI 是命令行的"壳"）。

### 2.1 窗口

- 标题 "PCSMT2"；尺寸 = 屏幕宽/2+160 × 屏幕高/2+90，位置 = (屏幕宽/4−80, 屏幕高/4−45)（约屏幕中央）。
- 图标：优先 PIL `ImageTk.PhotoImage` 加载 `<base>/static/PCSMT2.ico`（`wm iconphoto`），ImportError 或其他异常回退 `root.iconbitmap`，再失败仅记日志。
- `_get_base_path`：frozen 时若 `_MEIPASS` 存在用之；**否则 base_path 变量可能未定义**（见 bug 列表）；非 frozen 时取 `__file__` 上三级目录。
- 背景色 `#a6c9ff`；ttk 主题 `winnative`。
- 通过 monkey-patch 给 `tk.Canvas` 增加 `create_rounded_rectangle`（polygon smooth=True 画圆角矩形）。
- 初始化顺序：`bind_rounded_rectangle()` → `create_widgets()` → `redirect_logging()` → `execute_command('about')` → `mainloop()`（**mainloop 在 `__init__` 中阻塞**）。

### 2.2 布局组件（自上而下）

1. **按钮栏**（ttk.Frame，style "Card.TFrame"）：4 个用 Canvas 绘制的圆角"按钮"（100×35，填充 #e0e7ff、描边 #4a86e8、Arial 10 bold，悬停变 #629dfc，点击事件绑在整个 canvas 上）：
   - **帮助** → `execute_command("help")`
   - **调试模式** → `execute_command("set debug true")`（cmd2 内置 set 命令）
   - **打开Web界面** → `open_web_interface()`：`webbrowser.open(f"http://127.0.0.1:{Info.Config.Port()}")`，并在日志框输出 `> 已打开Web界面: ...`
   - **退出** → `execute_command("exit")`（会走 `sys.exit(0)`，直接结束整个进程）
2. **日志区**（ttk.LabelFrame "日志输出"）：`scrolledtext.ScrolledText`，只读（state=DISABLED），bg #bcdbf8、fg #2B79EC、Consolas 10、insertbackground #2fee6f、selectbackground #3c7af7。
3. **分隔线**（ttk.Separator 水平）。
4. **命令输入区**（ttk.Frame "Cmd.TFrame"）：Label "输入命令:" + `ttk.Combobox`（width 50，postcommand=`update_autocomplete` 把 `cmd.get_all_commands()` 设为下拉值；样式 Modern.TCombobox，白底、padding 5）+ "执行" 按钮（Blue.TButton）→ `execute_current_command()`。
   - 绑定：`<Return>` 执行；`<Tab>` 补全；`<Up>`/`<Down>` 历史遍历。
5. **状态栏**：右侧 Label `PCSMT2 v{Info.Config.PCSMT2_Version()}-{Info.Config.ReleaseVersion()}`（Segoe UI 8）。

### 2.3 交互行为

- **日志重定向**：自定义 `TextHandler(logging.Handler)` 附加到 `log.logger`，格式 `'%(asctime)s - %(levelname)s - %(message)s'`；同时 `sys.stdout`/`sys.stderr` 被全局替换为 `StdoutRedirector`（写入 log_text，flush 空实现，isatty=False）。
- **execute_command(command)**：先在日志框回显 `>>> {command}`，然后临时把 sys.stdout/sys.stderr 和 `self.cmd.stdout`（若存在）替换为重定向器，调用 `self.cmd.onecmd(command)`，finally 恢复。**异常不捕获**（onecmd 抛错会冒出）。
- **Tab 补全**：解析当前文本，`parts[0]` 为命令；若有 `complete_<command>` 方法则调用（text=最后一个 token，line=全文，begidx/endidx 按文本长度计算），否则按命令名前缀匹配。唯一结果 → 直接补全并加空格；多结果 → 设为下拉值并 `event_generate('<Down>')` 展开。返回 "break"。补全函数抛异常 → 记 `补全错误: {e}`，completions=[]。
- **历史**：`command_history` 列表，新命令 `insert(0, ...)`（去重只查第 0 项）；Up 键 `history_index += 1`（向更早方向），Down 递减到 -1 时清空输入。
- 全局 `sys.stdout` 重定向发生在 `redirect_logging()`（构造时），而 execute_command 内又套一层临时重定向——GUI 运行期间控制台 print 全部进日志框。

## 3. bootstrap 初始化流程（bin/bootstrap.py）

1. `get_base_path_inlet(relative_path="")`：frozen 时用 `os.path.dirname(sys.executable)`，否则取 `__file__` 上两级（项目根）。`run_bootstrap()` 开头 `os.chdir(base_path)`——之后所有相对路径都以项目根为基准。
2. 大段被注释掉的"防多开"代码（psutil + pygetwindow，IsProgramRunning，若同进程数 >1/2 则置顶已有窗口并 exit）。
3. 导入 `bin.export.{Java, Examine, log}`。初始化 `java_versions_address = {"1.8":"","16":"","17":"","21":""}`。
4. **Java 检查循环**：`versions = [1.8, 16, 17, 21]`（**1.8 是 float**），对每个版本 `Examine.Java.Exist(version)`：
   - 已安装 → 对每个 path/ver 记录 `✅ 版本: {ver}已安装`；
   - 未安装 → 记录错误后尝试 `Java.Install.Windows(version)`；失败提示手动安装；成功则 `java_versions_address[f'{version}'] = version`（**注意存的是版本号而非路径**——疑似 bug）。
5. 读 `java_versions.json` 覆盖 `java_versions_address`；对空字符串条目，扫描 `C:\Program Files\Java` 下目录名含 `jdk{version}`（小写匹配）的第一个目录，拼出 `...\bin\java.exe`；找不到则调 `Java.Install.Windows(javas)` 并把返回值当路径存入。文件不存在 → 记录错误"正在创建java_versions.json文件..."。
6. 把 `java_versions_address` 写回 `java_versions.json`（indent=4）。
7. 导入 `bin.export.{Info, Init, timer}` + `threading`；`timer.TimerStorageSizeUpdate.thread()`（后台定时更新存储大小）；`Init.Infomation.Program()`（初始化程序信息，注意 "Infomation" 拼写）。
8. 导入 `bin.command.Program` 与 `bin.api.main`；`Program.Do.CreateShortCut('PCSMT2-v' + Info.Config.PCSMT2_Version(), False)`（创建快捷方式）。
9. `Key.Generate.Key()`（生成密钥，用于 API 加密）。
10. 管理员账户：`Admin.Examine.IsExistAdminAccount()` 为假 → 用 `input()` 交互式询问账号名和密码（**明文输入，不用 getpass**），`Admin.Set.AdminAccount(name, password)`。
11. 启动 Flask API 后台线程：`threading.Thread(target=main.run_flask, daemon=True).start()`。bootstrap 本身不启动 CLI/GUI（由调用方负责）。

## 4. config.json 完整内容

```json
{
    "PCSMT2_Version": "1.2.2.1.3",
    "ReleaseVersion": "Release",
    "RunningMemories_Min": 2048,
    "RunningMemories_Max": 4096,
    "Nogui": true,
    "WaitEulaGenerateTime": 25,
    "AutomaticStartup": false,
    "AutoUpdateSource": "Github",
    "MinecraftTestVersion": false,
    "StorageSizeUpdateTime": 1800,
    "Port": 40000
}
```

（端口默认 40000；更新源配置值 "Github" 首字母大写，而 CLI 补全提供小写 'github'/'gitee'——大小写不一致。）

## 5. java_versions.json 完整内容

```json
{
    "1.8": "C:\\Program Files\\Java\\jdk1.8.0_452\\bin\\java.exe",
    "16": "C:\\Program Files\\Java\\jdk1.8.0_452\\bin\\java.exe",
    "17": "C:\\Program Files\\Java\\jdk17.0.15_6\\bin\\java.exe",
    "21": "C:\\Program Files\\Java\\jdk21.0.7_6\\bin\\java.exe"
}
```

注意："16" 指向 jdk1.8.0_452（当前机器无 JDK16，落入了 bootstrap 的目录名子串匹配误报——见 bug 列表）。

## 6. requirements.txt 完整依赖清单

```
flask>=2.0.3
requests>=2.28.1
openpyxl>=3.1.2
cryptography>=38.0.4
pygetwindow>=0.0.4
pywin32>=306
psutil>=5.9.4
Pillow>=9.4.0
packaging>=21.3
pyinstaller>=5.11.0
pyperclip>=1.8.2
winshell>=0.6
python-dotenv>=0.21.1
urllib3>=1.26.14
cmd2>=4.0.0
mcrcon>=0.7.0
tqdm>=4.64.1
```

（tkinter 未列出，属标准库；index.html 声称依赖 Python 3.13.2。）

## 7. find_files 工具函数行为

### find_file.py

- `find_files_with_extension(directory, extension)`：`os.walk` 递归找所有 `endswith(extension)` 的文件，返回完整路径列表。无异常处理。
- `find_files_with_existence_and_create(directory)`：路径存在返回 True；不存在则 `open(directory,'w')` 创建空文件返回 True；OSError 记录"创建文件失败"返回 False。（父目录不存在会创建失败。）
- `find_files_with_existence(directory, msg=True)`：存在 True；不存在时 msg=True 则记录 error"文件不存在"，返回 False。
- `find_keyword_inline_and_change_argument(file_path, keyword, argument)`：读文件（utf-8，失败回退 ISO-8859-1，再失败打印并 return）；逐行找 `keyword in line`（**子串匹配**），把整行替换为 `keyword=argument\n`（**破坏注释/其他内容**，且会误匹配包含关键字的其他键，如 `spawn-protection` 会被 `spawn` 匹配）；有改动则 utf-8 写回并记 info，否则记 error；最后 debug 打印所有匹配行。
- `class Get: PropertiesKeys(FilePath, Keyword)`（静态风格方法但无装饰器）：读 utf-8 文件，返回**第一个**包含 Keyword 的行 `split('=')[1].strip()`；任何异常记 error 返回 False。（**无匹配时返回 None 而非 False；值中含 `=` 会截断**。）

### find_folder.py

- `find_folders_with_existence_and_create(directory)`：存在 True；不存在 `os.mkdir`（**非 makedirs**，父目录必须存在）成功 True，OSError 记"创建文件夹失败"后 `return`（即**返回 None 而非 False**）。
- `find_folders_with_existence(directory)`：存在 True；否则记 error 返回 False。

### tree.py

- `class Tree(root_dir)`：`GetTree()` 用 `pathlib.Path.rglob('*')` 递归收集所有路径（字符串），**追加到 self.tree（重复调用会累积重复项）**；`CurrentTree()` 用 `os.listdir` 返回当前层条目名列表（重置 self.tree）。两者均含目录与文件、无排序、无过滤。

## 8. introduction.py 行为

- 模块级常量：ProgramName="PCSMT (Plain Craft Server Management Terminal)"、PowerBy="Power by Ksayus"、Github/Gitee/Ksayus/Bilibili/个人网站 URL 字符串（含 `\t\t` 对齐）。
- `Homepage()`：打印 ASCII art banner、欢迎语、各主页链接（Github 前有 "My own homepage-->"）、`Version:{Info.Config.PCSMT2_Version()}-{Info.Config.Config['ReleaseVersion']}`（**注意同时用了函数和直接读 dict 两种方式**）。
- `Version()`：打印分隔线 + `Version:{PCSMT2_Version()}`。
- 有一段被注释的 `Homepage_GUI()`（引用了不存在的 `program_info.PCSMTVersion`，不可恢复使用）。

## 9. index.html（GitHub Pages 首页）概述

单文件中文营销页（lang="zh-CN"），标题 "PCSMT2 | 你的下一个Minecraft服务器"，图标 static/PCSMT2.ico。依赖 CDN：Bootstrap 5.3.0-alpha1 CSS/JS、Bootstrap Icons 1.10.3。结构：

- **Header**：蓝色渐变动画背景（gradientBG keyframes + 斜纹 animated-bg 层），大标题 PCSMT2，副标题"简单易用的Minecraft服务器管理终端"。
- **三大特性卡片**：服务器管理 / 核心下载（official、forge、fabric、mohist）/ API 接口。
- **项目介绍**：PCSMT-2(PlainCraftServerManagementTerminal-2)，Python 编写，依赖 Python 3.13.2；列出解决的四个痛点（多实例管理、远程控制、手动下载核心、手动改配置）。
- **核心功能**两列清单：创建/启动（网页启动）/下载核心/管理（封禁解封、OP、打开 mods/plugins 目录、改配置）/搜索本地服务器/快捷打开文件。
- **文档中心卡片**：链接 https://ksayus.github.io/PCSMT2-Docs/。
- **使用教程**：`help`、`help <command>`；三张 API 卡片：GET `127.0.0.1:5000/`、GET `127.0.0.1:5000/api/server`、GET `127.0.0.1:5000/api/program`（**注意写的是 5000，而 config 默认端口是 40000**——不一致）。
- **下载区**：按钮 href="#"，页面 JS fetch `https://api.github.com/repos/ksayus/PCSMT-2/releases/latest`，取 `assets[0].browser_download_url` 填入按钮（无 release/无 asset 时会抛 TypeError，仅 console.error）。
- **Footer**：GitHub 仓库、文档中心、Issues、API 文档链接；© 2025 PCSMT2。

## 10. 已知 bug 与怪癖汇总

1. **bootstrap：版本号 float**。`versions = [1.8, 16, 17, 21]` 中 1.8 是 float，`f'{version}'` → "1.8" 恰好能用，但 `Examine.Java.Exist(1.8)` 等下游收到的类型不一致。
2. **bootstrap：安装成功后存错值**。`java_versions_address[f'{version}'] = version` 存的是版本号而非 java.exe 路径。
3. **bootstrap：JDK 匹配误判**。`f'jdk{javas}' in jdk.lower()` 的目录名子串匹配导致 java_versions.json 中 "16" 错误指向 jdk1.8.0_452。
4. **bootstrap：Java 安装失败仍继续**。安装失败只记日志，程序继续初始化。
5. **bootstrap：管理员密码用 input() 明文输入**，且整个初始化在首次运行时阻塞等待 stdin——若 GUI/无控制台环境启动会卡死。
6. **bootstrap：`run_flask` 在 daemon 线程**，主线程退出即被杀；未传 host/port（应由 main 内部读 config）。
7. **commands.py：`arg.strip()` 外的 try/except ValueError 永远不触发**（str.strip 不抛 ValueError）——遍布 do_start_server、do_server_mods、do_stop_server 等约 10 处，空参数会直接传空串进后端。
8. **commands.py：min/max 内存比较是字符串比较**。`if argument_min > argument_max` 在 isdigit 校验后仍比较字符串："9" > "10" 为 True，会错误触发 swap（swap 后仍是字符串传给后端）。
9. **commands.py：`do_change_storage_size_update_time` 和 `do_change_port` 无 docstring**，help 列表中无说明；且两者的 ValueError 分支里 error 后没有 return，会继续 fall-through 调用后端（`Program.Change.Port(int(port))` 等）。
10. **commands.py：banned 用两个独立 if（无 else）**，players_or_ips 非 "ips"/"players" 时静默无操作；unban 用 if/elif 但同样无非法值报错。
11. **commands.py：`output_program_info` 的 help 写的是 `Command: out_program_info`**，与实际命令名不符；`build` 的 help 写 `Command: Build` 首字母大写。
12. **commands.py：exit 中 `sys.exit(0)` 后的 `return True` 不可达**；且 sys.exit 会杀死整个进程（GUI 中点"退出"亦然，finally 里的 stdout 恢复不会执行）。
13. **commands.py：补全函数中大量使用 `list`/`type` 作变量名**遮蔽内建；多个 complete_* 在无匹配分支返回 None（cmd2 通常容忍，但 GUI 的 on_tab_pressed 会把 None 当可迭代处理而进 except 分支记"补全错误"）。
14. **commands.py：`complete_add_server` 等补全在参数超界时隐式返回 None**（无兜底 return）。
15. **commands.py：`do_change_server_run_memories_config` 等 swap 后日志说"已自动调整最小内存为最大内存"，实际逻辑是交换两值**（描述与行为不符）。
16. **GUI：`_get_base_path` 在 frozen 但无 `_MEIPASS` 时 `base_path` 未定义** → UnboundLocalError。
17. **GUI：`__init__` 里直接 `mainloop()`**，构造即阻塞，无法实例化后做其他事。
18. **GUI：重定向 `sys.stdout/stderr` 后 bootstrap 阶段的 `input()`（管理员账户）无法工作**——依赖 bootstrap 先于 GUI 运行，否则首次运行创建管理员账号会卡死。
19. **GUI：execute_command 不捕获 onecmd 异常**；"调试模式" 按钮依赖 cmd2 的 `set` 命令存在。
20. **GUI：history_index 方向反直觉**：Up 增加 index 取更早命令（列表头是最新），index=-1 表示"未在历史中"，行为可用但易误读。
21. **find_file：`find_keyword_inline_and_change_argument` 子串匹配 + 整行覆盖**，会毁注释、误伤相似键（如 max-tick-time 含 "time"）；`Get.PropertiesKeys` 同样子串匹配且值中含 `=` 会被截断；无匹配返回 None，异常返回 False，调用方需区分三种返回。
22. **find_folder：创建失败返回 None 而非 False**，与文档"return: bool"不符；用 mkdir 而非 makedirs。
23. **tree.Tree.GetTree 重复调用累积旧结果**（不重置 self.tree）。
24. **配置不一致**：config.json 的 `AutoUpdateSource` 值 "Github"（大写 G）vs CLI 补全 'github'；index.html 文档写 API 端口 5000 vs config 默认 40000。
25. **index.html 下载按钮**：无 release asset 时 `data.assets[0]` 抛错且无 UI 反馈。
26. **introduction.Homepage 混用** `Info.Config.PCSMT2_Version()` 与 `Info.Config.Config['ReleaseVersion']` 两种访问方式。
