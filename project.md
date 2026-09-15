# PCSMT2 - Minecraft服务器管理终端

## 功能概述
- 🚀 多版本服务器部署（Vanilla/Forge/Fabric/Mohist）
- 📊 实时监控服务器资源使用情况
- 🔄 自动化备份与恢复系统
- 🌐 基于Flask的Web管理界面
- 📈 Excel报表生成功能
- 🔑 RCON协议安全连接
- ⚙️ 智能Java环境配置

## 安装指南
```bash
pip install -r requirements.txt
```

## 模块架构
### 核心模块
- `command/`: 命令执行体系
- `export/`: 数据导出处理
- `download/`: 资源下载管理
- `api/`: RESTful接口实现

## 使用说明
1. 配置Java环境路径
2. 通过Web界面创建服务器实例
3. 使用自动化部署功能
4. 监控服务器运行状态

## 开发文档
### 关键技术栈
- 多线程任务处理
- AES-256加密通信
- 注册表操作实现自启动
- 智能日志轮转机制

完整文档请参考各模块代码注释。
