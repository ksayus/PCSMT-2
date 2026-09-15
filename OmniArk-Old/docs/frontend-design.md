# OmniArk-Old 前端设计规范（Web 现代化重构）

> 目标：深色现代化管理面板。所有页面共享同一套设计令牌与交互规范。
> 技术约束：无构建步骤（纯 HTML/CSS/JS），CDN 引入 Bootstrap 5.3 + Bootstrap Icons + Chart.js。
> 品牌：OmniArk（副标题可保留 "PCSMT-2 重构版"）。图标 `/static/PCSMT2.ico`。

## 1. 设计令牌（所有页面共用，写入 main.css 并各页面引入）

```css
:root {
  --bg-primary: #0f1419;      /* 页面背景 */
  --bg-secondary: #1a1f27;    /* 卡片/面板背景 */
  --bg-tertiary: #242b36;     /* 悬停/输入框背景 */
  --border: #2d3542;
  --text-primary: #e6e9ef;
  --text-secondary: #9aa4b2;
  --accent: #4f8cff;          /* 主色调 */
  --accent-hover: #6ba0ff;
  --success: #3fb96c;
  --danger: #e5534b;
  --warning: #d9a038;
  --radius: 10px;
  --sidebar-width: 240px;
}
```

- 字体：系统字体栈 + `Consolas/JetBrains Mono` 用于终端/日志。
- 卡片：`var(--bg-secondary)` 背景、`1px solid var(--border)`、`border-radius: var(--radius)`、阴影 `0 2px 8px rgba(0,0,0,.25)`。
- 按钮：主按钮 accent 填充；危险操作（删除/停止）danger 描边或填充；全部圆角 8px、悬停过渡 0.15s。
- 状态徽章（badge）：运行中=success 圆点+文字；已停止=灰色。
- 所有交互反馈用右上角 Toast（Bootstrap Toast），禁止 alert()。

## 2. 布局

### 2.1 主控台（index.html，SPA）
- 左侧固定深色侧边栏（宽 240px，窄屏可折叠）：Logo + 导航（仪表盘 / 服务器 / 创建服务器 / 设置 / API 帮助）。
- 右侧内容区：顶部细条（页面标题 + 版本号），下方为动态内容。
- 前端 hash 路由：`#/dashboard`、`#/servers`、`#/servers/<name>`（详情：终端/统计/文件）、`#/create`、`#/settings`、`#/help`。

### 2.2 独立页面（login / create / settings / manager / chart）
同一套令牌 + 居中卡片（login/create）或顶部导航条（settings/manager/chart 需"返回主控台"链接）。

## 3. 页面功能与 API 对接（契约固定，不得改后端路由）

### 仪表盘 #/dashboard
- 资源卡片：CPU（`GET /api/program/get/CPU/Usage` → `{percent, freq_current, freq_max}`）、RAM（`GET /api/program/get/RAM/Usage` → `{percent, used_mb, total_mb}`）、磁盘（`GET /api/program/disk_usage` → `{used_percent, used_gb, total_gb, ...}`），环形或条形进度，5 秒轮询。
- 服务器概览：`GET /api/server/list` → `{serverlist: [...], serverCount: int}`；逐台 `GET /api/server/status/<name>` → `{status: "running"|"stopped", online: int}`。
- 最近启动：`GET /api/server/latest`（404 时显示"暂无记录"）。
- 版本：`GET /api/program/version` → `{version}`。

### 服务器列表 #/servers
- 卡片网格：每台显示名称、状态徽章、版本/大小/启动次数（`GET /api/server/info/<name>` → `{version, size, startCount, LatestStartedTime}`）。
- 操作按钮：启动 `POST /api/server/<name>/start`、停止 `POST /api/server/<name>/stop`、删除 `POST /api/server/delete/<name>`（删除需确认弹窗）、导出 Excel `POST /api/server/info/<name>/excel`（触发下载）、导出全部 `POST /api/server/list/excel`。
- 受保护操作需带 `X-Requested-With: XMLHttpRequest`；401 时跳 `/login`。

### 服务器详情 #/servers/<name>（或独立区块）
- 终端：日志区 `GET /api/server/get/<name>/terminal/logs`（返回纯文本或 `{logs}`，兼容两种）+ 命令输入 `POST /api/server/<name>/command` body `{command}` → `{success, message}`；自动滚动、3 秒轮询、仅运行时可发命令。
- 在线玩家：`GET /api/server/players/<name>`；封禁 `GET /api/server/get/banned/players/<name>`、`GET /api/server/get/banned/ips/<name>`；白名单 `GET /api/server/get/white-list/<name>`（`{success:false}` 表示未启用）；历史 `GET /api/server/get/history/players/<name>`。
- 存储折线图：Chart.js，数据 `GET /api/server/<name>/storage_info` → `{labels, values, type}`。（注意该路由在 server_api 中，若实际路径不同以 /server/<name>/storage_chart 页面所用为准——见 chart.js。）
- 入口链接：设置 `/server/settings/<name>`、文件管理 `/manager/<name>`、存储图表 `/server/<name>/storage_chart`。

### 创建服务器 #/create 与 /server/create
- 字段：serverName、coreType（official/forge/fabric/mohist）、coreVersion（`GET /api/program/minecraft_version` → `{minecraft_version: [...]}`，可搜索下拉）、port（1024-65535，默认 25565）、pvpEnabled、onlineMode、gameMode（survival/creative/adventure/spectator）。
- POST 表单到 `/server/create`（同步提交，显示现代化加载遮罩）。

### 设置 #/settings
- 读取 `GET /api/program/get/settings` → `{min_memory, max_memory, nogui_enabled, eula_wait_time, auto_start, update_source, test_versions, storage_update_time, server_port}`。
- 保存 `POST /api/program/set/settings`（JSON 同字段）→ `{success: true}`。表单用卡片分组 + 开关（checkbox switch）。

### API 帮助 #/help
- 从路由清单自动渲染或维护一份准确的表格（不得再硬编码过时路由）。

### /server/settings/<name>（服务器设置页）
- 读取 `GET /api/server/get/document/server.properties/<name>`（JSON 对象）与 `GET /api/server/get/run_memory/<name>` → `{min, max}`。
- 提交 `POST /api/server/set/settings/<name>`（FormData，字段：serverName, server-port, min-memory, max-memory, gamemode, difficulty, max-players, max-world-size, spawn-protection + 复选框 spawn-monsters/pvp/allow-flight/enable-command-block/white-list/online-mode/hardcore）。
- 分区卡片：基本设置 / 内存 / 游戏玩法 / 网络与安全。

### /manager/<name>（文件管理器）
- 双栏或单栏树状文件列表：`GET /api/manager/<name>/list?path=<rel>` → `{path, entries: [{name, is_dir, size, modified}]}`。
- 操作（全部 POST JSON）：create/file、create/folder `{path}`；delete/file、delete/folder `{path}`；rename `{path, new_name}`；copy、move `{src, dst}`（字段名以 omniark/interfaces/web/routes/manager_api.py 实际解析为准，写前端前先读它！）。
- 面包屑导航、文件大小人性化、目录优先排序、操作前确认弹窗。

### /server/<name>/storage_chart
- Chart.js 折线图 + 时间范围统计卡片（最新/最大/平均）。

### /login
- 深色居中卡片，字段 admin_account/admin_password，错误提示 `{{ error }}`，回车提交。

## 4. 交互规范
- fetch 统一封装：`api(path, options)`，自动加 `X-Requested-With` 头、统一错误 Toast、401 跳登录。
- 所有按钮操作后刷新相关数据；启动/停止中给按钮 loading 态（禁用 + spinner）。
- 删除类操作一律确认弹窗（Bootstrap Modal）。
- 响应式：< 992px 侧边栏折叠为汉堡菜单。

## 5. 明确禁止
- 禁止 alert()/confirm() 原生弹窗；禁止内联大段样式（样式进 CSS）；禁止 alert 式错误吞掉；不得修改任何后端路由路径与响应结构。
