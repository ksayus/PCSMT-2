# PCSMT-2 `bin/command` 行为规格文档（重构用）

> 分析范围：`bin/command/Server.py`（1467 行）、`Program.py`（536 行）、`Manager.py`（119 行）、`Start.py`（19 行），以及它们直接依赖的 `bin/export/*`、`bin/find_files/*`、`bin/download/Core.py`（仅用于补全副作用与数据格式）。
> **重要前置条件**：代码中大量使用嵌套引号 f-string（如 `f'{ServerInfo['Path']}...'`），**只能在 Python ≥ 3.12（PEP 701）下运行**。全部为 Windows 专用（`winreg`、`win32com`、`winshell`、`taskkill`、`start` 命令）。

---

## 0. 全局基础设施（被四个文件共用的关键依赖）

### 0.1 路径常量（`bin/export/Info.py`）

`work_path = os.getcwd()`（**运行时当前工作目录**，非脚本目录，重构时必须注意）。

| 常量 | 值 | 说明 |
|---|---|---|
| `Info.File.Folder.Save` | `\saves` | 服务器信息 json 目录 |
| `Info.File.Folder.ServerStorageSize` | `\server_storage_size` | 存储大小历史目录 |
| `Info.File.Folder.Logs` | `\logs` | 程序日志目录 |
| `Info.File.Folder.Mods` | `\mods` | 服务器 mods 子目录 |
| `Info.File.Folder.Plugins` | `\plugins` | 服务器 plugins 子目录 |
| `Info.File.Folder.Servers` | `\servers` | 默认新建服务器根目录 |
| `Info.File.Folder.Resource` | `/resource` | **正斜杠**（不一致） |
| `Info.File.Folder.CoreInstallation` | `/core_installation` | |
| `Info.File.Folder.Excel` | `/excel` | |
| `Info.File.Document.StartBatch` | `\start.bat` | 服务器启动批处理文件名 |
| `Info.File.Document.Eula` | `\eula.txt` | |
| `Info.File.Document.ServerProperties` | `\server.properties` | |
| `Info.File.Document.Config` | `\config.json` | 程序配置文件 |
| `Info.File.Document.DeleteOldProgram` | `\delete_old_program.bat` | 自动更新残留清理脚本 |
| `Info.File.Document.Latest` | `/latest.txt` | 最近启动信息（**work_path 根**） |
| `Info.File.Document.Latest_json` | `/latest.json` | 被两处以不同前缀使用（见 bug 清单） |
| `Info.File.Document.Latest_log` | `/latest.log` | 服务器日志 |
| `Info.File.Document.banned_player` | `/banned-players.json` | |
| `Info.File.Document.banned_ip` | `/banned-ips.json` | |
| `Info.File.Document.op` | `/ops.json` | |
| `Info.File.Document.ForgeServerStartBatchDefaultName` | `/run.bat` | Forge 服务端启动脚本 |
| `Info.File.Document.ForgeServer_JVM_args` | `@user_jvm_args.txt` | Forge JVM 参数占位符 |
| `Info.File.Document.ServerInfoExcel` | `/AllServerInfo.xlsx` | |
| `Info.File.Document.WhiteList` | `/whitelist.json` | |
| `Info.File.Document.UserCache` | `/usercache.json` | |
| `Info.RCON.LocalHost()` | `127.0.0.1` | RCON 主机（硬编码） |
| `Info.RCON.Password()` | `pcsmt2` | RCON 密码（**硬编码**） |

其他：`program_name = 'PCSMT2'`；`ProjectRepository.Github/Gitee` 为 releases API URL。

### 0.2 config.json 默认结构（`Info.Config.Config`）

```json
{
  "PCSMT2_Version": "1.2.2.1.3",
  "ReleaseVersion": "Release",
  "RunningMemories_Min": 1024,
  "RunningMemories_Max": 2048,
  "Nogui": true,
  "WaitEulaGenerateTime": 30,
  "AutomaticStartup": true,
  "AutoUpdateSource": "Github",
  "MinecraftTestVersion": false,
  "StorageSizeUpdateTime": 3600,
  "Port": 5000
}
```

`Info.Config.*` 均为 classmethod，惰性调用 `Init.Infomation.Config()` 读取 config.json，失败时回退默认值。`Info.Information` 在 **import 时**就执行 `Server.Get.List(ShowMessage=False)`、`Get.Info.MinecraftVersion()`（联网！）、`Get.Info.PropertiesKeys()` —— import Info 模块即有文件扫描与网络请求副作用。

### 0.3 依赖模块速览

- `log.py`：import 时创建 `logs/<年>/<月>/<日>/` 目录并新建 `<时-分-秒>.log` 文件句柄；`log.Debug()` 仅在非打包（非 exe）时输出。`log.now_time` 为当前日志文件名前缀。
- `find_file.find_files_with_extension(dir, ext)`：`os.walk` 递归，返回**完整路径**列表（`os.path.join(root, file)`）。`ext=''` 时匹配所有文件。
- `find_file.find_files_with_existence_and_create(path)`：文件不存在则**创建空文件**。
- `find_file.find_keyword_inline_and_change_argument(file, keyword, argument)`：逐行**子串**匹配，命中行整行替换为 `keyword=argument\n`，utf-8 失败回退 ISO-8859-1。
- `find_folder.find_folders_with_existence_and_create` / `find_folders_with_existence`：注意后者在文件夹**不存在**时也会 `log.logger.error`（噪音）。
- `size_change.size_change(bytes)` → `"123.45MB"` 形式字符串（ROUND_HALF_UP，两位小数，单位 B/KB/MB/GB/TB）。
- `Get.Info.DirSize(path)`：递归 `os.scandir` 求字节总数。
- `GetTime.TimeString.DetailedTime()` → `"2020/01/01/00:00:00"`；`Auto_Time()` 按 config 的 `StorageSizeUpdateTime` 选择精度（见 2.2）。
- `Examine.Server.InfoKeys(server_name)`：读取 `saves/<name>.json`，**补全缺失字段并立即写回文件**，异常返回 `False`（详见 2.1）。
- `Eula.Examine.IsAgree(server_info)`：重写 eula.txt，`eula=false` → `eula=true`（且 `server_info['Counts'] += 1`），返回 server_info。
- `Java.Get.JavaVersion(Version)`：读 `./java_versions.json`（键 `'1.8'/'16'/'17'/'21'` → java.exe 路径），按 MC 版本返回**带双引号**的 java 路径字符串。
- `RCON.*`：`Get.RCON_Object(port)` 用 mcrcon 连接 `127.0.0.1:port`、密码 `pcsmt2`，**每次创建都会先 `with` 连接一次并发送 `/say Hello from RCON! I'm PCSMT2!`**，然后返回一个**已关闭的** MCRcon 对象（调用方再 `connect()` 重连）；失败返回 `False`。`Set.RCON(server_info)` 改 server.properties：`enable-rcon=true`、`rcon.port=server-port+10`（越界则 -10）、`rcon.password=pcsmt2`，返回端口。`Infomation.EnableRCON` 返回字符串 `'true'/'false'`。
- `IsProgramRunning.Do.taskkill(name, 'cmd.exe')`：枚举所有窗口，标题包含 `name` 且进程名含 `cmd.exe` 的，`os.system('powershell taskkill /F /PID <pid>')`。
- `timer.TimerStorageSizeUpdate`：每服务器一个 daemon 线程周期更新存储大小（详见 2.2）。`timer.Heartbeat_instance`：**import timer 模块即启动** daemon 心跳线程（4 秒周期），维护 `{'Name': [...], 'Online': [...]}`。

---

## 1. `bin/command/Server.py` 完整清单

### 1.1 `class Processing`（服务器生命周期）

#### `Processing.Add(Path, server_name, rewrite, Version, CoreType)` — 添加已有服务器
- **参数**：`Path` 服务器目录；`server_name`；`rewrite` bool 是否覆盖同名；`Version` MC 版本字符串；`CoreType`。
- **返回**：无（None）。
- **流程**：
  1. `Path = os.path.abspath(Path)`。
  2. 递归扫描 `Path` 下所有 `.jar`（完整路径列表 `Core`）。0 个 → 报错返回。
  3. >1 个时，循环 `len(Core)` 次执行同一过滤（冗余）：剔除路径中含以下任一**子串**的条目：`server.jar, com, commons-io, cpw, de, io, it, org, trove, java, jodah, mincraftforge(拼写错误), minecrell, sf, net, org.apache, org.apache.commons, org.apache.logging.log4j(.core/.lookup/.config/.appender)`。过滤后为空 → 报错返回。取 `Core[0]`。
  4. 确保 `work_path\saves` 目录存在；确保 `<Path>\start.bat` 存在（不存在创建空文件）。
  5. 写 start.bat：
     - 第 1 行：`cd <Path>`
     - 若存在 `<Path>/run.bat`（Forge）：读取其中第一行含 `java` 且不含 `--onlyCheckJava` 的行，把 `@user_jvm_args.txt` 替换为 `-Xms<min>M -Xmx<max>M`，把子串 `java` 替换为 `JavaVersion(Version)` 结果；找不到则用默认命令。
     - 否则默认命令：`<java_args> -Xms<min>M -Xmx<max>M -jar <Core完整路径>`
     - `Nogui` 为真追加 ` -nogui`；末尾写 `\nexit`。
  6. 确保 `<Path>\eula.txt` 存在并写入 `eula=true`（无条件覆盖）。
  7. 计算 `server_size = size_change(DirSize(Path))`。
  8. 若 `saves/<server_name>.json` 已存在：`rewrite=True` → **读出再原样写回（无任何修改，伪"覆盖"）**；`rewrite=False` → 报错返回。
  9. 不存在则创建并写入服务器信息 dict（结构见 2.1，`Counts=0`，`LatestStartedTime='N/A'`），成功后调用 `timer.TimerStorageSizeUpdate.thread()` 重启存储统计线程组。
  10. **兜底**：若之后 `saves/<server_name>.json` 仍不存在，再写一次相同结构（此处引用的 `server_size/AbsolutePath` 可能未定义，见 bug 清单）。
  11. `Info.Information.ServerList.append(server_name)`（**不去重**）。
- **副作用文件**：`<Path>\start.bat`（写）、`<Path>\eula.txt`（写）、`saves/`（建目录）、`saves/<name>.json`（建/写）；副作用线程：重启全部存储统计线程。

#### `Processing.Build(server_name, core_type, core_support_version)` — 创建新服务器
- **返回**：None。
- **流程**：
  1. 尝试 `Examine.Server.InfoKeys(server_name)` 读取已有信息。若目录 `server_info['Path']` 存在且**非空**（用 `find_files_with_extension(path, '')`，空扩展名匹配一切），进入 `while(1)`：给 `Name`/`Path` 追加 `-repeat`（Path 先 `rstrip('\\')`），创建新目录，直到目录为空 break。
  2. `Core.Processing.DownloadCore(server_name, core_type, core_support_version)` 成功 → 调 `Processing.Add(server_info['Path'], server_info['Name'], True, version, type)`。**注意：下载用的是原 `server_name`，Add 用的可能是 `-repeat` 名/路径（bug，见后）**。
  3. 若第 1 步抛异常（服务器不存在）：创建 `work_path\servers\<server_name>` 目录 → `DownloadCore` → 成功则 `Processing.Add(save_core_path, server_name, False, ...)`，刷新 `Info.Information.ServerList = Get.List()`，并 `timer.TimerStorageSizeUpdate.thread()`。
- **DownloadCore 外部调用**（`bin/download/Core.py`）：
  - fabric：`os.system('powershell java -jar <work>/resource/core_installation/fabric-installer.jar server -mcversion <v> -downloadMinecraft -dir "<work>\servers\<name>"')`，然后把 `fabric-server-launch.jar` 重命名为 `<server_name>.jar`。
  - forge：`os.system('java -jar <work>/resource/core_installation/forge-installer.jar --installServer "<dir>"')`，之后**删除安装器 jar**。
  - official：`requests.get('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json')` → 取版本详情 → `os.system('powershell curl -o <dir>\official-server.jar <url>')`。
  - mohist：`requests.get('https://mohistmc.com/api/v2/projects/mohist/<v>/builds')` 取最后一个 build → `powershell curl -o <dir>\mohist-server.jar <url>`。
  - 其他 core_type：仅报错，返回 None（隐式）。

#### `Processing.Delete(server_name, double_check)` — 删除服务器
- **返回**：`True` 成功 / `False` 失败或取消。
- **流程**：读信息 → `double_check=True` 时要求 3 次机会内输入正确服务器名，再二次 `y/n` 确认 → `shutil.rmtree(server_info['Path'])` 删除整个服务器目录 → `os.remove(saves/<name>.json)`。**不清理** `server_storage_size/<name>.json`，不更新内存中的 `ServerList`。

#### `Processing.Retracement(server_name, backup_file_name=None)` — 回档
- **返回**：`False` 失败 / None 成功（无显式 True）。
- **内部函数**：`get_top_level_dirs(zip_path)`（取 zip 首级目录名；**在 `with` 块外继续使用已关闭的 `zf`**）；`remove_readonly`（rmtree 的 onerror，chmod 去掉只读）。
- **流程**：`Get.FindBackupFile(server_name)` 返回 `[备份文件名..., 'mod'|'plugin']`（最后一个元素是类型标记）。
  - `backup_file_name=None`：取 `backups[-2]` 为文件名。
  - **mod 分支**：备份路径 `<Path>/backups/<file>`；先对每个首级目录"备份"到 `<Path>/old-save.zip`（**循环内每次以 'w' 模式重建 zip → 只剩最后一个条目；arcname 是绝对路径**），再 `shutil.rmtree` 删旧目录，最后 `extractall(<Path>)`。
  - **plugin 分支**：备份路径 `<Path>/plugins/eBackup/backups/<file>`；对 zip 内**每个条目**（含文件）做同样 old-save.zip 处理，仅当条目恰好是已存在的文件夹时才 rmtree，然后解压。
- 异常仅打印 `解压文件失败` 并返回 False。

### 1.2 `class Do`

#### `Do.Ban.Player / Do.Ban.Ip(server_name, name_or_ip)` — 封禁
- 流程：`Examine.Server.InfoKeys` → `RCON.Get.Port(server_info)` 读 server.properties 的 `rcon.port` → `RCON.Get.RCON_Object(port)`（失败/无 `connect` 属性即返回）→ `time.sleep(1)` → `connect()` → `command('/ban <name>')` 或 `command('/ban-ip <ip>')` → `disconnect()`。
- **返回**：None。**副作用**：每次执行都会在服务器广播一次 `/say Hello from RCON! I'm PCSMT2!`（RCON_Object 的固有副作用）。

#### `Do.Unban.Player / Do.Unban.Ip` — 同上，命令为 `/pardon <name>`、`/pardon-ip <ip>`。

#### `Do.Set.Op / Do.Set.Deop` — 同上，命令为 `/op <name>`、`/deop <name>`。

#### `Do.Open.Mods_Plugins_Folders(server_name)`
- 若 `<Path>\mods` 或 `<Path>\plugins` 存在，分别用 `Start.Open.File`（`os.system("start <path>")`）打开两个文件夹（两个都尝试打开，独立 try）。都不存在则报错"服务器是否启动过一次以上"。

#### `Do.Start(server_name)` — 启动服务器（核心流程，详见第 6 节）
- **返回**：`True` / `False` / None（混乱，见 bug 清单）。

#### `Do.Stop(server_name)`
- 读信息 → `EnableRCON` 为字符串 `'false'`：`IsProgramRunning.Do.taskkill(server_name, 'cmd.exe')` 杀标题含服务器名的 cmd 窗口 → 返回 None。
- 否则 RCON 发 `/stop`，成功返回 `True`；各失败分支返回 None 或 False（不一致）。

#### `Do.StartLatest()`
- 读 `work_path/resource/latest.json`（注意是 Resource 前缀），取 `Name` 调 `Do.Start`，成功返回 `server_info` dict，失败返回 False/None。

#### `Do.Restart(server_name)`
- `Do.Stop` → `sleep(3)` → `Do.Start`。**不检查两者结果**，总是打"重启服务器成功"，返回 None。

### 1.3 `class Get`（Server.py 内）

| 函数 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `List(ShowMessage=True)` | — | `list[str]` 服务器名 | 扫 `saves/*.json`（递归 os.walk）；跳过 0 字节与 JSON 解析失败的文件；缺 `Name` 字段时尝试用旧键 `server_name` 补全并写回文件，失败填 `None` |
| `Search(server_name, Output=True)` | — | `dict` / `False` / None | 读单个 json；缺 `Version` 补 `'N/A'`；`Output=True` 时逐项 log 输出（**源码注释写反了**） |
| `FindBackupFile(server_name)` | — | `list`（末尾带 `'mod'`/`'plugin'` 标记）/ None | mods 内含 `ftbbackups2` → 列 `<Path>/backups` 按 mtime 排序、剔除含 `.json` 的条目，追加 `'mod'`；plugins 内含 `'ebackup'`（**小写敏感**）→ 列 `<Path>/plugins/eBackup/backups` 不排序，追加 `'plugin'` |
| `Properties(server_name)` | — | **生成器** yield `(keyword, value)` | 对 55 个 properties 关键字逐个从 server.properties 取值 |
| `RunMemory(server_name)` | — | `{'Xms': list[str]\|0, 'Xmx': list[str]\|0}` / False | 正则 `-Xms(\d+)`、`-Xmx(\d+)` 匹配 start.bat 全文；**找不到返回 int 0 而非空列表（类型不一致）** |
| `TerminalLogs(server_name, lines, block_size=1024)` | — | `str` / False | 二进制倒序分块扫描 `<Path>\logs/latest.log`，取最后 `lines` 行，utf-8 errors='ignore' 解码 |
| `BannedPlayers(ServerInfo)` | dict（**类型注解误标为 str**） | `list[str]` / False | 读 `<Path>/banned-players.json`，取每项 `name` |
| `WhiteList(ServerInfo)` | 同上 | `list[str]` / False | 先看 server.properties `white-list=true`，是则读 `whitelist.json`；未开启返回 False（与异常同值，无法区分） |
| `HistoryPlayers(ServerInfo)` | 同上 | `list[str]` / False | 读 `usercache.json` 取 `name` |
| `CurrentPlayers(ServerInfo)` | 同上 | 在线信息 / False | 从 `timer.Heartbeat_instance.GetList()` 的 `{'Name':[], 'Online':[]}` 按名字索引取 `Online[i]`（其值为 `[在线数, 最大数, [玩家...]]` 或 False） |

### 1.4 `class Change`（Server.py 内）

| 函数 | 行为 |
|---|---|
| `Properties(server_name, keyword, argument)` | 对 `<Path>\server.properties` 做子串行替换 `keyword=argument`。无校验、无返回值 |
| `RunningMemories(server_name, memory_min, memory_max)` | 重写 start.bat：`cd <Path>` + `<java_args> -Xms.. -Xmx.. -jar <Core>` + 可选 ` -nogui`。**不写 `exit` 行**（与 Add 不一致）；**丢失 Forge run.bat 形式的启动命令**，变成纯 `-jar` 命令 |
| `Rename(server_name, new_name)` | 改 dict 的 `Name`；`os.rename` saves 下 json 文件；写回。**不重命名服务器文件夹**，不同步内存 ServerList |
| `Redirected(server_name, new_path)` | 字符串替换 `Core`、`StartBatchPath` 中的旧路径为 `new_path`（不移动任何实际文件），重写 json 和 start.bat（含 `exit`）。异常分支日志自相矛盾（见 bug 清单） |

---

## 2. 数据格式

### 2.1 `saves/<服务器名>.json`（服务器信息文件）

由 `Processing.Add` / `Examine.Server.InfoKeys` 写入，`indent=4`：

```json
{
    "Name": "MyServer",
    "Counts": 3,
    "Core": "D:\\Project\\PCSMT-2\\servers\\MyServer\\paper-1.20.4.jar",
    "Path": "D:\\Project\\PCSMT-2\\servers\\MyServer",
    "StartBatchPath": "D:\\Project\\PCSMT-2\\servers\\MyServer\\start.bat",
    "Size": "1.23GB",
    "Version": "1.20.4",
    "LatestStartedTime": "2025/06/01/12:30:00",
    "CoreType": "official"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | str | 服务器名（与 json 文件名一致） |
| `Counts` | int | 启动次数；首次启动前为 0 |
| `Core` | str | 核心 jar 的**完整绝对路径**（不是文件名！来自 `os.path.join`） |
| `Path` | str | 服务器目录绝对路径（反斜杠结尾风格混杂） |
| `StartBatchPath` | str | start.bat 绝对路径 |
| `Size` | str | 人类可读大小，如 `"512.34MB"`（由 timer 周期刷新） |
| `Version` | str | MC 版本，如 `"1.20.4"`；缺失补 `'N/A'` |
| `LatestStartedTime` | str | `"YYYY/MM/DD/HH:MM:SS"` 或 `'N/A'` |
| `CoreType` | str | `fabric/forge/official/mohist` 或 `'N/A'` |

**旧字段兼容**（`Examine.Server.InfoKeys` 读取时的回退键）：`server_name→Name`、`start_count→Counts`、`server_core→Core`、`server_path→Path`、`server_start_batch_path→StartBatchPath`、`server_version→Version`、`server_size→Size`（都没有则用默认值/现算）。**每次读取都会补全并写回文件**——读操作有写副作用。

### 2.2 `server_storage_size/<服务器名>.json`

由 `timer.TimerStorageSizeUpdate.every_time_update_server_storage_size` 维护：

```json
{
    "storage_size": ["100.0MB", "105.32MB"],
    "time": ["2025年-06月-01日-12时", "2025年-06月-01日-13时"]
}
```

- 两个**平行数组**：`storage_size[i]` 对应 `time[i]`。
- 空文件/解析失败/空 dict → 重置为两个空数组。
- 每条记录同时把最新值写回 `saves/<name>.json` 的 `Size` 字段。
- `time` 字符串精度由 config 的 `StorageSizeUpdateTime`（秒）决定（`GetTime.TimeString.Auto_Time`）：<60 秒→到秒；60~3600→到分；3600~86400→到时；86400~604800→到日；604800~2592000→到月；2592000~31536000→到年。**恰好 60 秒或 ≥31536000 秒时所有分支不命中，返回 None**（bug）。
- 去重逻辑仅当 `0 < StorageSizeUpdateTime < 1555200`（18 天）时生效：与最后一条相同则跳过。
- 定时器结构：`thread()` 对 `Info.Information.ServerList` 每个服务器建一个 daemon 线程，循环 `StopTimerStorageSizeUpdate.wait(1)` 倒数到 0 后更新。**停止事件是全类共享的**——`set()` 会停掉所有服务器的线程。线程名是默认 `Thread-N`（不是 `start_timer`）。

---

## 3. `bin/command/Program.py` 完整清单

### 3.1 `class Change`（全部读写 `work_path\config.json`，读-改-写模式）

| 函数 | 参数 | 修改键 | 返回 | 备注 |
|---|---|---|---|---|
| `RunningMemories_Config(argument_min, argument_max)` | int, int | `RunningMemories_Min/Max`（强转 int） | True/False | config 缺失返回 False |
| `Nogui(argument)` | bool | `Nogui` | True/False/**None** | 同步 `Info.Config.Nogui = argument`（**给 classmethod 覆盖成普通属性**） |
| `WaitEulaGenerateTime(argument)` | int | `WaitEulaGenerateTime` | True/False/None | 同上覆盖 classmethod |
| `AutoStartup(argument)` | bool | `AutomaticStartup` | True/False/None | 同上 |
| `MinecraftTestVersion(argument)` | bool | `MinecraftTestVersion` | True/False/None | 第 174 行刷新版本列表的语句**不可达**（bug） |
| `StorageSizeUpdateTime(time)` | int(秒) | `StorageSizeUpdateTime` | True/False/None | 尝试停旧定时线程再重启（**线程名匹配失败，见 bug**）；内层异常分支 `False` 缺 `return` |
| `Port(argument)` | int | `Port` | True/False/None | |
| `UpdateSource(argument)` | str `'Github'/'Gitee'` | `AutoUpdateSource` | True/False/None | 无取值校验 |

### 3.2 `class Do`

| 函数 | 行为 |
|---|---|
| `AddStartup(name, file_path="")` | 写注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`，值=程序路径（默认 `sys.argv[0]` 真实路径）。`auth="IvanHanloth"` 为死变量 |
| `RemoveStartup(name)` | 删除上述注册表值，找不到仅 print |
| `ShortCut(program_version, icon=True, description=True)` | 用 `WScript.Shell` COM 在桌面创建 `PCSMT2.lnk`，指向 `work_path/<program_version>.exe`，描述"我的世界服务器管理终端" |
| `CreateShortCut(program_version, recoverage)` | `recoverage=True` 强制重建；否则桌面（`~/Desktop`）无同名 lnk 才创建 |

### 3.3 `class Processing`

- **`Restart(program_name)`**：写 `work_path\delete_old_program.bat`，内容：
  ```bat
  @echo off
  if "%1" == "h" goto begin
  start mshta vbscript:createobject("wscript.shell").run("""%~nx0""h",0)(window.close)&&exit
  :begin
  timeout /t 5
  cd <work_path>
  powershell rm <work_path>/PCSMT2-v<PCSMT2_Version>.exe
  start <program_name>
  exit
  ```
  然后 `os.system("start <work_path>\delete_old_program.bat h")`，sleep 后 `sys.exit()`。（mshta 提权隐藏窗口技巧）
- **`Delete_Script()`**：删除上述 bat。

### 3.4 `class Output`
- `ProgramInfo()`：log 输出程序名与 `Info.Config.ConfigRead`（类型注解字典，不是实际配置——怪癖）。

### 3.5 `class Format`
| 函数 | 行为 |
|---|---|
| `Log()` | 遍历 `logs/<年>/<月>/<日>/` 四层：删除非当前 `now_time.log` 的文件；删除非当日的日期目录、非当月目录、非当年目录（`shutil.rmtree`） |
| `Settings()` | 把 `Info.Config.Config` **默认值**写回 config.json（重置配置） |
| `Server()` | 名为"移除服务器"，**实际代码与 Settings 完全相同**（重置 config.json，不动任何服务器文件）——复制粘贴 bug |
| `Latest()` | 清空 `work_path/latest.txt` 与 `work_path/latest.json`（**与 Do.Start 写入的 `work_path/resource/latest.json` 不是同一文件**） |
| `Program()` | 交互确认后依次调 Log→Server→Latest→Settings |

### 3.6 `class Get`
| 函数 | 返回 |
|---|---|
| `CPU_Usage()` | `(cpu_percent, 当前频率MHz, 最大频率MHz)`（psutil，interval=1 阻塞 1 秒；docstring 描述错误） |
| `RAM_Usage()` | `(占用百分比, 已用MB)` |

---

## 4. `bin/command/Manager.py` 完整清单

`class Manager` 两个嵌套类，全部为**实例方法**（需 `Manager.File()` 实例化），**全部无异常处理，成功恒返回 True**：

| 类 | 方法 | 实现 | 返回 |
|---|---|---|---|
| `File` | `Delete(file_path)` | `os.remove` | True |
| | `Move(cur, target)` | `shutil.move` | True |
| | `Copy(cur, target)` | `shutil.copy` | True |
| | `Rename(cur, target)` | `os.rename` | True |
| | `Search(file_path, file_name)` | `Tree(file_path).GetTree()`（`Path.rglob('*')` 全递归），子串匹配；**对每个不匹配项也打 info 日志（极吵）**；结果存 `self.search_result` | list[str] |
| | `Create(file_path)` | 以 'w' 打开即关（**截断已有文件**） | True |
| | `Status(file_path)` | `os.stat` → `{'size': st_size, 'mod_time': 'YYYY-MM-DD HH:MM:SS'}` | dict |
| `Folder` | `Delete(folder_path)` | `shutil.rmtree` | True |
| | `Create(folder_path)` | `os.makedirs` | True |
| | `Status(folder_path)` | 同 File.Status（**目录 st_size 非递归总大小，几乎无意义**） | dict |
| | `Rename(old, new)` | `os.rename` | True |
| | `Copy(old, new)` | `shutil.copytree`（目标存在会抛错） | True |
| | `Move(old, new)` | `shutil.move` | True |

`import os/time` 在文件中导入但 `time` 仅 Status 使用；`Tree.GetTree()` 多次调用会**在 self.tree 上累积**（不清空，bug）。

---

## 5. `bin/command/Start.py` 完整清单

- `class Open` → `Open.File(file_path)`：`os.system("start " + file_path)`，返回码 0 打 info 否则 error。
- **怪癖**：路径未加引号，**含空格路径直接失败**；`start` 的返回码不可靠；参数名与内置无关但文件路径拼接时若首参数带引号会被当作窗口标题。

---

## 6. 外部调用汇总

| 位置 | 调用 | 命令/目标 |
|---|---|---|
| `Start.Open.File` | `os.system` | `start <file_path>` |
| `Program.Processing.Restart` | `os.system` | `start <work>\delete_old_program.bat h` |
| `IsProgramRunning.Do.taskkill` | `os.system` | `powershell taskkill /F /PID <pid>` |
| `Core.DownloadCore` fabric | `os.system` | `powershell java -jar <work>/resource/core_installation/fabric-installer.jar server -mcversion <v> -downloadMinecraft -dir "<dir>"` |
| `Core.DownloadCore` forge | `os.system` | `java -jar <.../forge-installer.jar> --installServer "<dir>"` |
| `Core.DownloadCore` official/mohist | `os.system` | `powershell curl -o <dir>\<name>.jar <url>` |
| `Examine.Java.Version` | `subprocess.run` | `[<java_path>, '-version']`（timeout=5，解析 stderr 的 `version "x.y.z"`） |
| `Java.Install.Windows` | `subprocess.run` | `setx JAVA_HOME ... /M`、`setx PATH ... /M`；`requests.get` corretto.aws JDK zip；`ctypes ShellExecuteW runas` 提权 |
| `Get.Info.MinecraftVersion` | `requests.get` | `https://launchermeta.mojang.com/mc/game/version_manifest.json`（timeout=10） |
| `Core.DownloadCore` official | `requests.get` | `https://piston-meta.mojang.com/mc/game/version_manifest_v2.json` |
| `Core.DownloadCore` mohist | `requests.get` | `https://mohistmc.com/api/v2/projects/mohist/<v>/builds` |
| `Program.Do.AddStartup/RemoveStartup` | `winreg` | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| `Program.Do.ShortCut` | `win32com` | `WScript.Shell` 创建桌面 lnk |
| RCON 全部 | `mcrcon.MCRcon` | `127.0.0.1:<rcon.port>`，密码 `pcsmt2` |

---

## 7. 服务器启动流程（`Do.Start(server_name)`）完整步骤

1. 校验 `work_path\saves\<name>.json` 存在，否则返回 False。
2. `Examine.Server.InfoKeys(name)` 读取并补全信息；设 `LatestStartedTime = DetailedTime()`（"YYYY/MM/DD/HH:MM:SS"）。
3. `Start.Open.File(server_info['StartBatchPath'])` → `os.system('start <start.bat路径>')` 弹出 cmd 窗口运行启动脚本。失败返回 False。
4. sleep 2 秒。
5. **首次启动（`Counts == 0`）**：sleep `WaitEulaGenerateTime`（默认 30 秒）等待 eula 生成；若 `<Path>\eula.txt` 存在 → `Eula.Examine.IsAgree(server_info)`（把 `eula=false` 改写为 `eula=true`，并把 `Counts+1`）；不存在 → 报错返回 False。
   **非首次（`Counts >= 1`）**：直接 `IsAgree`。
6. `Counts += 1` 后写回 `saves/<name>.json`（注意 IsAgree 里可能已加过一次，**首启且 eula=false 时 Counts 一次加 2**）。
7. 读 `<Path>\server.properties` 找 `server-port` 行，`int(split('=')[1])` 得 `server_port`；文件不存在 → 返回 **None**（不是 False）。
8. `RCON.Infomation.EnableRCON` 读 `enable-rcon`：
   - 为字符串 `'false'`：`port = 0`。
   - 否则 `RCON.Set.RCON(server_info)`：写 `enable-rcon=true`、`rcon.port=server-port+10`（越界改 -10）、`rcon.password=pcsmt2`。
   - 然后进入 `while not ConnectStatus` 循环：反复 `RCON_Object(Port)` + connect/disconnect，失败 sleep 2 重试，**无超时、无 break（被注释），服务器起不来则死循环**。
9. 写 `work_path\latest.txt`：
   ```
   服务器名称:<name>
   <str(server_info)>
   服务器端口:<server_port>
   RCON端口:<port 或 "未启用">
   启动时间:<DetailedTime>
   ```
10. 更新 `LatestStartedTime`，把 server_info 写入 `work_path\resource\latest.json`（`find_files_with_existence_and_create`，目录需已存在否则 open 失败被吞）。
11. log 输出端口与 `127.0.0.1:<port>`，返回 True。

**start.bat 内容（Processing.Add 生成）**：
```bat
cd <服务器目录>
"<java.exe路径>" -Xms1024M -Xmx2048M -jar <核心jar完整路径> -nogui
exit
```
（Forge 则是改造后的 run.bat 命令行；`Change.RunningMemories` 重写的版本**没有 exit 行**。）

**eula 处理**：`Add` 时直接写死 `eula=true`；`Start` 时若服务器自己生成了 `eula=false` 则重写为 `eula=true`（逐行复制其余行）。

---

## 8. 已知 Bug 与怪癖清单（重构必须修复/保留决策点）

### 严重 / 功能性
1. **`Do.Start` RCON 连接死循环**：`while not ConnectStatus` 无超时无 break（第 818 行 break 被注释）。
2. **`Do.Start` 返回值混乱**：True / False / None（server.properties 读取失败分支是裸 `return`）；`Stop`、`Search`、`Restart` 同样 None/False 混用。
3. **`serverCount` 显示 bug（`Get.List`）**：`'当前服务器数量：'` 用的是 `len(server_list)`（**扫描到的 json 文件总数**），而实际返回的 `server_lists` 只含有效条目（空文件/解析失败/无名文件被跳过）——两者可不一致。
4. **`Get.List` 缺 Name 分支**：自动填充失败后 `now_server_name` 未绑定，随后引用抛 `UnboundLocalError`（被外层 except 吞掉，该文件静默丢失）。
5. **`Processing.Add` rewrite=True 是伪覆盖**：读出原 json 再原样写回，Version/CoreType/Path 等全不更新。
6. **`Processing.Add` 兜底块（196–214 行）**：在前面分支失败时引用可能未定义的 `server_size`、`AbsolutePath`，抛 `NameError`（未捕获）。
7. **`Info.Information.ServerList` 不去重**：`Add` 每次 append，重复添加同名服务器会积累重复项，导致 timer 为同一服务器起多个线程。
8. **`Program.Change.StorageSizeUpdateTime` 停线程逻辑失效**：匹配 `'start_timer' in thread.name`，但线程名是默认 `Thread-N`——旧线程永不停，每次修改配置**叠加一整套新定时线程**。
9. **`TimerStorageSizeUpdate.StopTimerStorageSizeUpdate` 是类级共享 Event**：任何一处 `set()` 停掉所有服务器的统计线程。
10. **`Processing.Build` 的 `-repeat` 逻辑**：下载用原名目录、Add 用 `-repeat` 路径，核心文件根本不在被扫描目录里（功能错位）；且修改的是局部 dict 的 Name，json 文件名与 Name 会不一致。
11. **回档 `old-save.zip` 逻辑报废**：循环内每次 `'w'` 模式重建 zip → 只保留最后一个条目；`arcname` 用绝对路径 → zip 内是完整盘符路径；`get_top_level_dirs` 在 `with` 块外使用已关闭的 ZipFile。
12. **`Get.FindBackupFile` plugin 分支大小写敏感**：`'ebackup' in plusins` 匹配不到实际目录 `eBackup`（Windows 返回真实大小写）→ plugin 备份永远找不到（除非恰好全小写）。
13. **`Format.Server()` 名不符实**：代码与 `Format.Settings()` 完全相同（重置 config.json），**不删除任何服务器**。
14. **`Format.Latest()` 清错文件**：清 `work_path/latest.json`，而 `Do.Start`/`StartLatest` 用的是 `work_path/resource/latest.json`。
15. **java_versions.json 版本区间有洞**（`Java.Get.JavaVersion`）：恰好 `1.17.0`、`1.20.5`、`>1.21.8` 均不命中任何分支 → 返回空字符串，start.bat 变成 `"" -Xms...`；`Version='N/A'` 时 `packaging.version.parse` 直接抛异常。且用相对路径 `./java_versions.json` 打开（依赖 cwd）。
16. **`GetTime.TimeString.Auto_Time` 区间空洞**：`StorageSizeUpdateTime == 60` 或 `>= 31536000` 时返回 None，写入 json 的 time 数组出现 `null`。
17. **`Change.RunningMemories` 丢 Forge 启动命令**：一律改成 `-jar` 直启，且缺 `exit` 行。
18. **RCON 命令带前导斜杠**（`/ban`、`/stop` 等）：部分核心对 RCON 命令的 `/` 处理不一致（原版服务端 RCON 通常应不带 `/`）。
19. **`RCON.Get.RCON_Object` 副作用**：每次获取对象都会向服务器广播 `/say Hello from RCON! I'm PCSMT2!`；且返回的是 `with` 块关闭后的对象，依赖调用方重新 connect。

### 轻微 / 风格
20. `Processing.Add` 排除关键字循环 `for i in range(len(Core))` 内不使用 `i`，同一过滤重复执行 N 次；关键字含 `mincraftforge` 拼写错误、`org` 重复；**子串匹配作用于完整路径**，路径中含 `com`/`net`/`java` 等常见词（如用户名 `Javadeveloper`）会误删核心。
21. `os.path.abspath(AbsolutePath)` 结果被丢弃（第 87 行）。
22. `Examine.Server.InfoKeys` **读操作带写副作用**（补字段并写回），且 `log.logger.error` 用于提示正常缺字段，噪音大。
23. `Program.Change.*` 系列把 `Info.Config.Nogui = argument` 等**覆盖 classmethod 为普通属性**，破坏惰性加载语义；多个函数 config 不存在时返回 None 而非 False。
24. `Program.Change.MinecraftTestVersion` 第 174 行（修改成功后刷新版本列表）不可达；`StorageSizeUpdateTime` 内层异常分支是裸 `False`（无 return）。
25. `Manager.File.Create` 会截断已有文件；`Tree.GetTree` 多次调用结果累积；`Folder.Status` 的 size 无意义；所有 Manager 方法无异常处理。
26. `Start.Open.File` 路径不加引号，含空格路径必失败。
27. `Eula.Examine.IsAgree` 在异常分支也 `Counts += 1`，与 `Do.Start` 的 `+1` 叠加导致计数失真。
28. `Get.RunMemory` 找不到时返回 int `0` 而非列表（类型不一致）；`WhiteList` 用 False 同时表示"未开启"和"出错"。
29. `Heartbeat` 在 **import timer 时**即起线程；`GetList()` 依赖 `self.HeartbeatInstance`（未调 `thread()` 前不存在——但模块底部已调，属于隐藏的全局时序耦合）。
30. `log.Debug` 在打包 exe 下是空操作，排错信息随打包丢失；`timer` 异常处理用 `log.logging.error`（误打 root logger，应为 `log.logger`）。
31. 大量 f-string 嵌套同种引号（`f'{ServerInfo['Path']}'`）——**锁定 Python ≥ 3.12**。
32. `IsProgramRunning.Is.Running()` 返回的是**计数**而非文档声称的 bool。
33. `Processing.Delete` 不删除 `server_storage_size/<name>.json`（残留），不同步内存 `ServerList`；`Change.Rename` 不同步 `ServerList` 与 `latest.json`。
