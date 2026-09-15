# PCSMT-2 Web 层行为规格文档（重构用）

> 范围：`bin/api/`（Flask 应用）、`bin/download/`（核心下载/Excel 导出/自动更新）、`templates/` + `static/`（前端）。
> 辅助参考：`bin/export/Info.py`（常量）、`bin/export/Admin.py`（鉴权后端），因被直接依赖而一并纳入。

---

## 0. 总览

- 项目：PCSMT2 —— Minecraft 服务器管理工具（Windows，PyInstaller 打包）。
- Web 框架：Flask（开发服务器 `app.run`），无蓝图（Blueprint），所有路由通过 `bin.api.main.app` 单例注册。
- 前端：服务端渲染模板 + 静态 JS（fetch AJAX）。主页面 `index.html` 是 SPA 风格的单页（侧边栏 + 动态内容区），其余为独立页面。

---

## 1. Flask 应用结构

### 1.1 应用初始化（`bin/api/main.py`）

- `resource_path(relative_path)`：兼容 PyInstaller（`sys._MEIPASS`）与源码运行（`os.path.abspath(".")`）。
- `app = Flask(__name__, template_folder=resource_path('templates'), static_folder=resource_path('static'))`
- **`app.secret_key = 'pcsmt2'`**（硬编码，安全弱点）。
- 若 `IsProgramRunning.Is.Running()` 为真（程序已打包运行），禁用 werkzeug 请求日志：`logging.getLogger('werkzeug').disabled = True`。
- `run_flask()`：延迟 import 所有路由模块（`api, api_server, api_program, api_resource_manager, PageServer, PageProgram, Resouce, ServerSocket`）以完成注册，然后 `app.run(port=Info.Config.Port())`。默认端口 5000（config.json 的 `Port`）。
- 注意：未设置 `host`，默认仅监听 127.0.0.1。

### 1.2 配置常量（`bin/export/Info.py`，路由行为的依赖）

- 目录：`File.Folder.Servers='\servers'`、`Resource='/resource'`、`CoreInstallation='/core_installation'`、`Excel='/excel'`、`Logs='\logs'` 等。
- 文件：`Latest_json='/latest.json'`、`ServerInfoExcel='/AllServerInfo.xlsx'`、`WhiteList='/whitelist.json'`、`banned_player='/banned-players.json'` 等。
- 核心安装器保存路径：`Core.Position.fabric_core_installation_save='/resource/core_installation/fabric-installer.jar'`，`forge_core_installation_save='/resource/core_installation/forge-installer.jar'`。
- 核心默认文件名：`Core.DefaultName`: Fabric=`/fabric-server-launch.jar`，Forge=`/forge-installer.jar`，Official=`/official-server.jar`，Mohist=`/mohist-server.jar`。
- 仓库 API：`ProjectRepository.Github = "https://api.github.com/repos/ksayus/PCSMT-2/releases/latest"`；`Gitee = "https://gitee.com/api/v5/repos/ksayus/PCSMT-2/releases/latest"`。
- 默认配置：版本 `1.2.2.1.3`，`ReleaseVersion=Release`，内存 1024/2048MB，`Nogui=True`，`WaitEulaGenerateTime=30`，`AutomaticStartup=True`，`AutoUpdateSource=Github`，`MinecraftTestVersion=False`，`StorageSizeUpdateTime=3600`，`Port=5000`。
- `work_path = os.getcwd()`（**依赖启动时的工作目录**）。

### 1.3 全部路由清单

#### `bin/api/api.py` — 根路由

| 方法 | 路径 | 说明 | 返回 |
|---|---|---|---|
| GET | `/` | 主页 | `render_template('index.html')` |
| GET | `/api` | API 首页 | HTML 字符串 `<h1>Welcome to PCSMT2 API!</h1>` |

#### `bin/api/api_program.py` — 程序信息/设置

| 方法 | 路径 | 参数 | 后端调用 | 返回 JSON |
|---|---|---|---|---|
| GET | `/api/program` | — | — | HTML 欢迎字符串 |
| GET | `/api/program/version` | — | `Info.Config.PCSMT2_Version()`、`Config['ReleaseVersion']` | `{"version": "<ver>-<ReleaseVersion>"}`；错误 500 `{"error": "获取程序信息时发生内部错误"}` |
| GET | `/api/program/minecraft_version` | — | `Info.Information.MinecraftVersion` | `{"minecraft_version": [...]}`；500 错误 |
| GET | `/api/program/disk_usage` | — | `Get.Info.DiskUsage()` → 四元组 | `{"disk_usage", "disk_free", "usage", "free"}`；500 |
| GET | `/api/program/get/settings` | — | 直接读 `./config.json` | `{min_memory, max_memory, nogui_enabled, eula_wait_time, auto_start, update_source, test_versions, storage_update_time, server_port}`（映射自 config 键 `RunningMemories_Min/Max, Nogui, WaitEulaGenerateTime, AutomaticStartup, AutoUpdateSource, MinecraftTestVersion, StorageSizeUpdateTime, Port`）；500 |
| POST | `/api/program/set/settings` | JSON body：`min_memory, max_memory, nogui_enabled, eula_wait_time, auto_start, update_source, test_versions, storage_update_time, server_port` | 依次调用 `Program.Change.RunningMemories_Config / Nogui / WaitEulaGenerateTime / AutoStartup / UpdateSource / MinecraftTestVersion / StorageSizeUpdateTime / Port` | 成功 `{"success": true}`；500 `{"error": "更新设置时发生内部错误"}` |
| GET | `/api/program/get/CPU/Usage` | — | `Program.Get.CPU_Usage()` → (percent, freq_now, freq_max) | `{"success":true,"message":"获取CPU占用率成功","used":percent,"total":freq_max,"abs_used":round(freq_now,2),"abs_total":round(freq_max,2)}`；**异常时裸 `return`（返回 None → Flask 500 TypeError）** |
| GET | `/api/program/get/RAM/Usage` | — | `Program.Get.RAM_Usage()` → (percent, MB) | `{"success":true,...,"used":percent,"total":MB,"abs_used":MB,"abs_total":round(MB/(percent/100),2)}`；异常裸 return；**percent=0 时 ZeroDivisionError** |

#### `bin/api/api_server.py` — 服务器管理（核心）

| 方法 | 路径 | 鉴权 | 说明 / 后端调用 | 返回 |
|---|---|---|---|---|
| GET | `/api/server` | 无 | API 首页 | HTML 字符串 |
| GET | `/api/server/list` | 无 | `Server.Get.List(ShowMessage=False)` | `{"serverlist": [...], "serverCount": str(ServerList)}` —— **bug：serverCount 是整个列表的 str，不是数量**；500 |
| GET | `/api/server/players/<ServerName>` | 无 | `timer.Heartbeat_instance.GetList()` → 在 `Name[]` 中找索引取 `Online[i]` | `{"server": name, "players": status}`；数据空 500 `{"error":"数据为空"}`；未找到 404 `{"error":"服务器不存在"}` |
| GET | `/api/server/info/<server_name>` | 无 | `Server.Get.Search(name, True)` | 404 `{"error":"服务器不存在"}`；或 200 `{version, size, startCount, LatestStartedTime}`（来自 `server_info['Version'/'Size'/'Counts'/'LatestStartedTime']`） |
| GET | `/api/server/latest` | 无 | 读 `work_path + /resource + /latest.json` | `{name, version, size, startCount, LatestStartedTime}`；若文件不存在 **`return False`（非法响应，Flask 会抛 500）**；若 JSON 缺 `LastStartTime` 补 `'N/A'`（但响应里用的是 `LatestStartedTime` 键，补的键没用上） |
| GET/POST | `/api/server/<server_name>/start` | **admin_required** | `Server.Do.Start(name)` | 200 `{"status":"starting"}`；502 `{"error":"error"}`；500 `{"error":"内部错误"}` |
| GET/POST | `/api/server/<server_name>/stop` | **admin_required** | `Server.Do.Stop(name)` | 200 `{"status":"stopped"}`；502；500 |
| GET | `/api/server/<server_name>/storage_info` | 无 | `Get.Info.StorageSize(name)` → `{storage_size: [...], time: [...]}`；把 "5.2GB" 剥离单位为 float 数值 | `{title: "<name>服务器存储情况", labels: time[], values: float[], type: TB/GB/MB/KB/B}`；400 `{"error":"未找到信息"}`；500 |
| GET | `/api/server/status/<server_name>` | 无 | `Examine.Server.InfoKeys(name)` + `RCON.Infomation.ServerStatus(ServerInfo)` | 运行中：200 `{"status":"starting","message":"服务器已启动"}`；未运行：**502** `{"status":"stopped","message":"服务器未启动"}`（用 502 表示“停止”语义不当） |
| POST | `/api/server/info/<server_name>/excel` | 无 | `Download.Excel.SignalSheet(name, ServerInfo)` → GenerateFile/WriteData/FilePath | `send_file(path, as_attachment=True)` 下载 xlsx；500 `{"error":"生成文件失败"}` |
| POST | `/api/server/list/excel` | 无 | `Download.Excel.MultiSheet(server_list)` 同上 | xlsx 附件；500 |
| POST | `/api/server/delete/<server_name>` | **admin_required** | `Server.Processing.Delete(name, False)` | 200 `{"status":"deleted"}`；502 `{"error":"删除错误"}`；500 |
| GET | `/api/server/get/document/server.properties/<server_name>` | 无 | `Server.Get.Properties(name)`（返回键值对序列） | JSON 对象 `{key: value, ...}`；格式非法的项记 warning 跳过 |
| GET | `/api/server/get/run_memory/<server_name>` | 无 | `Server.Get.RunMemory(name)` → `{'Xms','Xmx'}` | `{"min": Xms, "max": Xmx}` |
| POST | `/api/server/set/settings/<server_name>` | 无 | 表单字段见下；`Server.Change.Properties(...)` ×13 + `Server.Change.RunningMemories` + `Server.Change.Rename` | 200 `{"message":"修改成功"}`；500 |
| GET | `/api/server/get/<server_name>/terminal/logs` | 无 | `Server.Get.TerminalLogs(name)` | **成功路径无 return（返回 None → 500）**；异常 `return False`（也是非法响应）——**整个路由是坏的** |
| POST | `/api/server/<server_name>/command` | 名义上 admin_required（**实际未生效，见 §2 bug**） | body JSON `{command}`；`RCON.Do.Command(ServerInfo, command)` | 服务器未启动 `{"success":false,"message":"服务器未启动"}`；成功 `{"success":true,"message": result}` |
| GET | `/api/server/get/banned/players/<server_name>` | 无 | `Server.Get.BannedPlayers(InfoKeys)` | `{"success":true,"message":"获取封禁玩家列表成功","BannedPlayerList":[...]}` |
| GET | `/api/server/get/white-list/<server_name>` | 无 | `Server.Get.WhiteList(InfoKeys)` | 未启用 `{"success":false,"message":"白名单未启用"}`；否则 `{"success":true,...,"WhiteList":[...]}` |
| GET | `/api/server/get/history/players/<server_name>` | 无 | `Server.Get.HistoryPlayers(InfoKeys)` | 空 `{"success":false,"message":"无历史玩家"}`；否则 `{"success":true,...,"HistoryPlayerList":[...]}` |

`/api/server/set/settings/<server_name>` 表单字段（`request.form`，复选框按 `'on'` 判断）：
`serverName, server-port(int), min-memory(int), max-memory(int), gamemode, difficulty, max-players(int), max-world-size(int), spawn-protection(int)`，复选框：`spawn-monsters, pvp, allow-flight, enable-command-block, white-list, online-mode, hardcore` → 转 `'true'/'false'` 字符串写入 server.properties。

#### `bin/api/api_resource_manager.py` — 文件管理器

| 方法 | 路径 | 说明 | 返回 |
|---|---|---|---|
| GET | `/manager/<server_name>` | `Server.Get.Search(name)`，不存在 404；渲染 `manager.html`（传 `server_info`，模板用到 `Path`、`Name`、`name`） | HTML |
| GET | `/api/get/directory?path=<path>` | 查询参数 `path`；先做 `replace('..','')` 防穿越（**可被绕过**），再 `urllib.parse.unquote`；不存在 404；`Tree(path).GetTree()/CurrentTree()` | `{"FilesCounts": len(All_dire), "CurrentDirectory": [...]}` |

注意：本模块 import 了 `Manager`（`bin.command.Manager`）但未使用；`manager.js` 调用的 `/api/manager/copy|move|rename|create/file|create/folder|delete/file|delete/folder` 路由在后端**完全不存在**。

#### `bin/api/PageServer.py` — 页面路由

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/server/create` | GET 渲染 `CreateServer.html`。POST 表单：`serverName, coreType, coreVersion, port, pvpEnabled, onlineMode, gameMode` → `Server.Processing.Build(Name, CoreType, CoreVersion)` → `Server.Do.Start(Name)` → **`time.sleep(40)`** → `Server.Do.Stop(Name)` → `time.sleep(3)` → 写 `server-port/pvp/online-mode/gamemode` 四项 properties → 渲染 `index.html`（同步阻塞约 43 秒） |
| GET | `/server/<server_name>/storage_chart` | 渲染 `chart_js.html`（只传 `server_name`，**未传模板引用的 `title`**） |
| GET | `/server/settings/<server_name>` | 渲染 `ServerSettings.html`（只传 `server_name`；模板里 `{{server_port}}`、`{{min_memory}}` 等变量均未传，实际由页面 JS 调 API 填充） |

#### `bin/api/PageProgram.py`

空文件（仅 import），**无任何路由**。

#### `bin/api/Resouce.py`（文件名拼写错误，应为 Resource）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/static/ico` | `send_from_directory('static', 'PCSMT2.ico')`（相对路径 `'static'`，打包路径下可能失败） |

#### `bin/api/ServerSocket.py` — 名为 Socket 实为 HTTP 的终端接口

| 方法 | 路径 | 说明 | 返回 |
|---|---|---|---|
| GET | `/api/server/terminal/<server_name>` | `ServerGet.TerminalLogs(server_name, 1000)`（最近 1000 行） | `{"success":true,"logs":[...]}`；500 `{"success":false,"error":str(e)}` |
| POST | `/api/server/terminal/<server_name>` | JSON body 必须含 `command` | **桩实现**：真正执行被注释，只返回 `{"success":true,"message":"命令 X 已发送到服务器 Y"}`；缺 command 时 400 |

#### `/login`（在 `api_server.py` 中）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET/POST | `/login` | GET 渲染 `login.html`。POST 表单 `admin_account/admin_password` → `Admin.Examine.Password(account, password)` → 成功 `session['authenticated']=True` 并 `redirect('/')`；失败重渲染 `login.html, error="账号或密码错误"` |

---

## 2. 鉴权机制

- **装饰器 `admin_required(f)`**（`api_server.py` L123–134，**未使用 `functools.wraps`**）：
  - 检查 `session['authenticated']`。
  - 未登录且请求头 `X-Requested-With: XMLHttpRequest` → 401 `{"error":"Unauthorized"}`（前端据此跳登录页）。
  - 未登录且非 AJAX → 把 `request.url` 存入 `session['next_url']` 后 `redirect(url_for('login'))`。
  - **`session['next_url']` 登录后从未被消费**；辅助函数 `is_safe_url(target)`（校验 netloc 防开放重定向）已定义但**从未被调用**。
- **登录流程**：`/login` POST → `Admin.Examine.Password`：账户文件在 `C:\PCSMT2-key\account\<account>.bin`，内容为 `Key.Do.CipherKey(password)` 加密的密码；验证 = 读文件 → `Key.Do.DecipherKey` 解密 → 明文比对。成功后写 session（依赖硬编码 `secret_key='pcsmt2'`）。
- **受保护路由**：`/start`、`/stop`、`/delete`。
- **重大 bug — `/api/server/<server_name>/command` 的保护失效**（L417–419）：

  ```python
  @admin_required            # ← 装饰器顺序错误
  @main.app.route(..., methods=['POST'])
  def execute_server_command(...)
  ```

  装饰器自底向上应用：`route` 先注册了**未包装**的原函数，之后 `admin_required` 包装出的 `wrapper` 从未注册到 Flask，因此该端点实际**无鉴权**。而其它受保护路由是 `@route` 在上 `@admin_required` 在下（正确顺序），但由于没有 `functools.wraps`，包装后函数名都变成 `wrapper`，只能靠显式 `endpoint='start_server'` 等避免端点命名冲突（`/command` 未显式指定 endpoint，恰好因顺序错误“逃过”冲突）。

---

## 3. `ServerSocket.py` 的“socket 通信协议”

**实际上不存在任何 socket 协议**。文件名为 ServerSocket，但内部只是两个普通 Flask HTTP 路由（见 §1.3）：

- 拉日志：`GET /api/server/terminal/<server_name>` → `{success, logs[]}`，前端 `main.js`（L1428）轮询该接口刷新终端视图。
- 发命令：`POST /api/server/terminal/<server_name>`，JSON `{command}` → **桩代码**，仅回显“已发送”，真正执行逻辑被注释（`Server.ExecuteCommand` 不存在）。
- 前端实际发命令走 `/api/server/<server_name>/command`（RCON 通道：`Examine.Server.InfoKeys` 取服务器信息，`RCON.Do.Command(ServerInfo, command)`，RCON 地址固定 `127.0.0.1`，密码固定 `'pcsmt2'`，见 `Info.RCON`）。

重构建议：此模块应替换为真正的 WebSocket（如 flask-sock）或删除，命令执行统一到 RCON。

---

## 4. download 模块：核心下载与安装

### 4.1 版本列表获取

- **前端**：`createserver.js` 调 `GET /api/program/minecraft_version` → `data.minecraft_version` 数组填充 `coreVersion` 下拉框。数据源为 `Info.Information.MinecraftVersion`（模块加载时由 `Get.Info.MinecraftVersion()` 一次性计算，定义在 `bin/command`/`bin/export`，不在本次范围；是否包含测试版由配置 `MinecraftTestVersion` 控制）。

### 4.2 各核心下载源与安装流程（`Core.py::Processing.DownloadCore(server_name, core_type, core_support_version)`）

所有下载均通过 `os.system('powershell curl -o <目标> <URL>')` 或 `os.system('java -jar ...')` 执行（**shell 拼接，存在注入风险与路径空格问题**）。

| 核心 | 版本/构建解析 | 下载源 URL | 安装流程 |
|---|---|---|---|
| **official** | `GET https://piston-meta.mojang.com/mc/game/version_manifest_v2.json` → 在 `versions[]` 找 `id == 版本` → 再 GET 该项 `url` → 取 `downloads.server.url` | Mojang piston-meta / piston-data | `powershell curl -o <work_path>\servers\<name>/official-server.jar <url>`（注意拼接缺 `\`：`Servers + '\' + name + DefaultName`，`DefaultName.Official='/official-server.jar'` 以 `/` 开头，Windows 上尚可工作） |
| **forge** | `CoreInstaller.Core.InitInstaller('forge', ver)`：`GET https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json` → `promos[ver + '-latest']` 得 forge 构建号 | `https://maven.minecraftforge.net/net/minecraftforge/forge/<mc>-<forge>/forge-<mc>-<forge>-installer.jar` → 存为 `/resource/core_installation/forge-installer.jar` | `java -jar <forge-installer.jar> --installServer "<work_path>\servers\<name>"`，随后 `os.remove` 删除安装器。成功 True |
| **fabric** | 安装器版本**硬编码 1.0.1**：先查 `/resource/core_installation/fabric-installer.jar` 是否已存在，不存在则下载 | `https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar` | `powershell java -jar fabric-installer.jar server -mcversion <ver> -downloadMinecraft -dir "<work_path>\servers\<name>"`；然后将默认产物 `<name>/fabric-server-launch.jar` **重命名为 `<name>\<name>.jar`**（路径拼接 `'\\'+name + DefaultName.Fabric` 中 DefaultName 以 `/` 开头） |
| **mohist** | `GET https://mohistmc.com/api/v2/projects/mohist/<version>/builds` → 取 `builds[-1].url`（最新构建） | Mohist 官方 API 返回的直链 | `powershell curl -o <work_path>\servers\<name>/mohist-server.jar <url>` |
| spigot | 已整段注释掉（BuildTools 方案），输入未知核心只记日志 `'输入的核心类型不正确'`（**隐式返回 None**） | — | — |

Forge 相关注释中保留的示例：installer URL 形如 `.../forge/1.16.5-36.2.42/forge-1.16.5-36.2.42-installer.jar`；版本 API `promotions_slim.json`。

### 4.3 Excel 导出（`Download.py`，类 `Excel`）

- **`SignalSheet(sheet=服务器名, ServerInfo)`**（单服务器）：
  - `GenerateFile()`：工作簿活动表名改为服务器名，创建第二表 `存储变化数据`，存到 `./resource/excel/<name>.xlsx`。
  - `WriteData()`：主表 A1–A10 标题（服务器名称/版本号/核心类型/上次启动时间/启动次数/存储占用/历史玩家/白名单玩家/封禁玩家/当前玩家），B 列写值，C 列起（`chr(67+i)`，**超过 23 人会越出字母表**）横向写玩家名；第二表写 `storage_size`/`time` 两列；之后 `Auto_Adapt()` 按 UTF-8 字节长度调列宽。
  - 数据来源：`Server.Get.HistoryPlayers/WhiteList/BannedPlayers/CurrentPlayers(ServerInfo)`（CurrentPlayers 取 `[2]` 索引）、`Get.Info.StorageSize(name)`。
  - `FilePath()` 返回绝对路径。
- **`MultiSheet(sheets=[服务器名...])`**：文件固定为 `./resource/excel/AllServerInfo.xlsx`，每个服务器一个 sheet，布局同上单表 + 从 A11 起内嵌存储数据；`Auto_Adapt()` 遍历各 sheet 调列宽（**bug：只改了内存对象，在 `WriteData` 里最后才 save，顺序为 Auto_Adapt→save，OK；但 SignalSheet.Auto_Adapt 是重新 load 文件再 save 的**）。
- 两个导出路由：`POST /api/server/info/<name>/excel`、`POST /api/server/list/excel`，均 `send_file(as_attachment=True)`。

---

## 5. `Update.py` 自动更新流程

入口在 `bin/export/Init.py`（启动时）：读配置 `AutoUpdateSource`（`Github`/`Gitee`），首选源失败（返回 False）时自动**回退另一源**。

- **Github**：`requests.get(Info.ProjectRepository.Github, verify=False)`（**关闭证书校验**且 `urllib3.disable_warnings()`）。
- **Gitee**：`requests.get(Info.ProjectRepository.Gitee)`（开证书校验）。
- 共同流程：
  1. 解析响应：`tag_name`（版本号串）、`name`（发布名，用作新 exe 文件名）。
  2. `packaging.version.parse` 比较本地 `Config['PCSMT2_Version']`（默认 `1.2.2.1.3`）与 `tag_name`。
  3. `v1 == v2` → 记“已最新”返回 `True`；`v1 < v2` → 进入下载；`v1 > v2` → 记日志返回 `None`。
  4. 取下载地址：GitHub 取 `assets[0]['browser_download_url']`；Gitee 遍历 `assets` 找第一个 `name.endswith('.exe')` 的 `browser_download_url`（**bug：若一个都没匹配，`download_url` 变量未定义，随后 `if download_url is None` 会抛 `UnboundLocalError`**）。
  5. 下载：`os.system('powershell curl -o "<work_path>/<name>.exe" <url>')`（Gitee 分支无引号）。
  6. `Program.Do.CreateShortCut(latest_version, True)` 创建新版本的快捷方式；`Program.Processing.Restart(latest_version)` 重启到新版本（旧版本清理由 `delete_old_program.bat` 机制负责）。
- 返回值语义混乱：True=已最新；False=网络/解析失败；下载成功/失败都返回 `None`。

---

## 6. templates / static 清单与页面结构

### 6.1 文件清单

**templates/**
- `index.html` — 主控台 SPA 外壳
- `login.html` — 管理员登录
- `CreateServer.html` — 创建服务器
- `manager.html` — 双栏文件管理器
- `ServerSettings.html` — 服务器配置编辑
- `chart_js.html` — 存储占用折线图

**static/**
- 图片：`PCSMT2.png`、`PCSMT2.ico`、`bilibili.png`、`loading.gif`
- CSS：`css/main.css`（全局+侧边栏）、`css/login.css`、`css/createserver.css`、`css/manager.css`
- JS：`js/main.js`（约 1754 行，主控台全部逻辑）、`js/login.js`（仅 Bootstrap 表单校验）、`js/createserver.js`、`js/manager.js`（文件管理器，调大量未实现的 `/api/manager/*`）、`js/chart.js`

### 6.2 页面结构概述

- **index.html + main.js**：左侧固定 `sidebar`（Logo、首页/服务器(动态下拉 `server-list`)/API帮助/设置），右侧 `#dynamic-content` 由 `pageContents` 映射（`home`/`help`/`servers`/`settings`）通过 `loadContent()` 注入。`home` 显示版本（`/api/program/version`）与 GitHub/Bilibili 链接；`help` 是**硬编码**的 API 列表表格（与真实路由有出入）；`servers` 拉 `/api/server/list` 渲染卡片，提供启动/停止/删除（带 `X-Requested-With: XMLHttpRequest` 头配合 401 跳转）、命令执行、封禁/白名单/历史玩家、终端日志轮询、Excel 导出、CPU/RAM/磁盘监控（`/api/program/get/CPU/Usage`、`get/RAM/Usage`、`disk_usage`）等功能。
- **login.html**：Bootstrap 5 表单，`admin_account`/`admin_password`，服务端注入 `{{ error }}`。
- **CreateServer.html**：表单字段 `serverName / coreType(official|forge|fabric|mohist) / coreVersion(JS 拉取) / port(1024–65535，默认 25565) / pvpEnabled(checkbox+hidden false) / onlineMode / gameMode(radio: survival/creative/adventure/spectator)`；提交为**同步表单 POST**，显示 `loadingOverlay`（因后端 sleep 40s+ 会长时间转圈）。
- **manager.html**：左右双面板（源/目标目录），工具栏按钮（新建文件/文件夹、删除、刷新、上级），中间复制/移动按钮；注入 `window.SERVER_PATH`、`window.SERVER_NAME`；模板引用 `/server/{{ server_info.name }}`（“返回服务器”，**该路由不存在**）。`manager.js` 调用的 `/api/manager/copy|move|rename|create/*|delete/*` 后端均未实现，**实际只有目录浏览（`/api/get/directory`）可用**。
- **ServerSettings.html**：内联 CSS + 表单（基本设置/内存/服务器属性三区），JS 加载时调 `/api/server/get/document/server.properties/<name>` 与 `/api/server/get/run_memory/<name>` 回填，提交到 `/api/server/set/settings/<name>`（FormData）。
- **chart_js.html**：Chart.js CDN，`<canvas id="storageChart">`；`chart.js` 调 `/api/server/<name>/storage_info`，用 `labels/values/type` 画折线图；模板引用 `{{ title }}` 但后端未传（渲染为空）。

---

## 7. 已知 Bug / 异味清单

1. **`serverCount` 返回 `str(ServerList)`**（`api_server.py` L31）——是整个列表的字符串化而非数量。
2. **`/api/server/<name>/command` 鉴权失效**——装饰器顺序错误（`@admin_required` 在 `@route` 之上），包装函数未注册；且 `admin_required` 未用 `functools.wraps`，靠显式 endpoint 名避免冲突。
3. **`/api/server/latest` 找不到文件时 `return False`**——非法 Flask 响应；补的 `LastStartTime` 键与响应所用 `LatestStartedTime` 不一致。
4. **`/api/server/get/<name>/terminal/logs`**——成功路径无返回值（None → 500），异常返回 False；与 `ServerSocket.py` 的 `/api/server/terminal/<name>` 功能重复且一方坏。
5. **CPU/RAM 接口异常路径裸 `return`**（None → 500）；RAM `abs_total` 在占用率 0% 时除零。
6. **`/api/server/status` 用 HTTP 502 表示“服务器已停止”** 的语义滥用；运行中状态字符串为 `"starting"` 而非 `"running"`。
7. **`/login` 的 `session['next_url']` 存而不用**；`is_safe_url()` 定义未用；`secret_key='pcsmt2'` 硬编码；无登出路由。
8. **`/server/create` POST 同步阻塞约 43 秒**（`time.sleep(40)+sleep(3)`），无超时/异步；成功后渲染 `index.html` 而非重定向（刷新会重复提交）。
9. **核心下载全部经 `os.system` + shell 字符串拼接**——命令注入、路径含空格/中文风险；official/mohist 路径拼接依赖 `DefaultName` 前导 `/` 在 Windows 的兼容行为；fabric 依赖外部 `powershell java`；official 下载后未重命名为 `<name>.jar`（与其它核心命名不一致）。
10. **Fabric 安装器版本硬编码 1.0.1**；Forge 每次重新下载安装器（Fabric 有缓存判断，Forge 没有）。
11. **Update.py**：GitHub `verify=False` 关证书校验；Gitee 分支 `download_url` 可能未定义（`UnboundLocalError`）；返回值语义不统一（True/False/None 混用）；下载成功即 `Program.Processing.Restart`，旧进程清理依赖外部 bat。
12. **manager.js 调用的 `/api/manager/*`（copy/move/rename/create/delete）后端全部未实现**；`api_resource_manager.py` import `Manager` 未用；manager.html 的“返回服务器”链接指向不存在的 `/server/<name>`；`/api/get/directory` 的 `replace('..','')` 防穿越可绕过且**未限制在服务器目录内**（任意目录可读）。
13. **`chart_js.html` 的 `{{ title }}`、`ServerSettings.html` 的 `{{server_port}}` 等模板变量后端未传**（靠 JS 兜底/显示空）。
14. **Excel 玩家列表用 `chr(67+i)` 生成列名**，超过 23 名玩家产生非法单元格地址；`MultiSheet.Auto_Adapt` 的列宽调整依赖 `log.Debug` 副作用之外无持久化问题但逻辑脆弱；`SignalSheet` 与 `MultiSheet` 大量重复代码。
15. **`PageProgram.py` 为空文件**；`Resouce.py` 文件名拼写错误；`Resouce.py` 中 `send_from_directory('static', ...)` 用相对路径，PyInstaller 打包后可能失效（应用 static_folder 已是 `resource_path` 处理过的绝对路径，此处没走它）。
16. **前端 `main.js` help 页的 API 表为硬编码**，与真实路由不一致（如 `/api/server/status` 缺参数、`/api/server/<name>/storage_chart` 写错了路径前缀等）。
17. `Info.work_path = os.getcwd()`：整个下载/资源路径依赖进程启动目录，工作目录变化即全坏。
18. `/api/server/set/settings` 与创建/删除/启停之外的写操作**无鉴权**（改 properties、改内存、重命名任何人均可调用）；storage_info、excel 导出、properties 读取等也无鉴权（视设计而定，但与 start/stop/delete 的保护策略不一致）。

---

以上规格覆盖了 `bin/api/`、`bin/download/` 全部代码路径及 templates/static 的结构与交互契约，可直接作为重构的对照基线。
