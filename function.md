# PCSMT-2 功能总结

## 一、当前实现功能
### 1. 服务器管理核心功能
- 服务器创建/配置
- 服务器启动/停止控制
- 内存配置修改（`change_server_run_memories_config`）
- 服务器路径重定向（`redirected_server_path`）
- 启动批处理文件自动生成

### 2. 玩家管理
- 玩家/IP封禁（`banned_ip`, `banned_players`）
- OP权限管理（赋予/取消`deop`）
- 玩家UUID自动查询（通过Mojang API）

### 3. 服务器文件管理
- mods/plugins文件夹快速访问
- 服务器核心文件管理（支持官方/Forge/Fabric/Mohist）
- 服务器信息持久化存储（JSON格式）

### 4. 程序配置管理
- 默认内存配置（`default_server_run_memories`）
- 自动更新源配置（Github/Gitee）
- 启动方式配置（`server_start_nogui`）
- 自动启动配置（`Automatic_startup`）

### 5. 维护功能
- 服务器删除（带二次确认）
- 日志文件管理
- 程序格式化（`format_program`）
- 配置重置（`Reset_settings`）

### 6. 系统集成
- Java环境检测与安装（`install_java_windows`）
- 启动器快捷方式创建
- 系统托盘自动启动配置

### 7. 在线更新
- GitHub/Gitee双源更新
- 自动检测新版本
- 在线安装程序更新

### 8. 信息输出
- 日志系统（`log.logger`）

## 二、未来规划功能（来自README）
1. **GUI界面**：可视化操作面板
2. **跨平台支持**：Windows/Linux/macOS
3. **增强管理功能**：
   - 服务器命令直接执行
   - 数据/配置/插件集中管理
   - 自动备份与恢复系统
   - 日志智能解析
4. **网络管理**：
   - RCON远程控制集成
   - 本地网页管理界面
5. **生态扩展**：
   - 更多服务器核心支持
   - 插件/MOD仓库集成

## 三、命令行命令清单