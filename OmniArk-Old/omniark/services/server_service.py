"""服务器生命周期管理：创建/注册/启动/停止/删除/重命名/重定向。

替代旧版 ``bin/command/Server.py``（1400+ 行嵌套静态类），
所有操作基于 :class:`ServerInstance` 实例，抛出具体异常而非返回 False/None。
"""

from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path

from omniark.core import paths
from omniark.core.config import get_config
from omniark.core.logger import get_logger
from omniark.exceptions import (
    CoreFileNotFoundError, OmniArkError, RconError, ServerAlreadyExistsError,
    ServerError, ServerNotFoundError, ServerRunningError,
)
from omniark.models.server import ServerInstance
from omniark.services import (
    core_downloader, java_service, process_manager, properties, rcon_service,
    registry,
)
from omniark.services.java_service import resolve_java_for_minecraft
from omniark.utils import process
from omniark.utils.files import directory_size
from omniark.utils.formatting import human_readable_size
from omniark.utils.timeutil import detailed_time

logger = get_logger()

# 筛选核心 jar 时排除的路径片段（旧版硬编码列表的合理化版本：
# 匹配 jar 文件名与库包路径片段，避免把 Forge 依赖库当成核心）
_CORE_EXCLUDE_KEYWORDS = (
    "commons-io", "cpw", "trove", "jodah", "minecrell", "installer",
    "org.apache", "log4j", "libraries",
)


# ------------------------------------------------------------ 创建 / 注册

def register_server(server_path: str | Path, server_name: str,
                    mc_version: str, core_type: str,
                    overwrite: bool = False,
                    root: Path | None = None) -> ServerInstance:
    """把一个已有的服务器目录注册进管理系统（旧版 Processing.Add）。

    流程：找核心 jar → 生成 start.bat → 写 eula → 算大小 → 写 saves JSON。
    """
    server_dir = Path(server_path).resolve()
    if not server_dir.is_dir():
        raise ServerError(f"服务器目录不存在: {server_dir}")
    if registry.server_exists(server_name, root) and not overwrite:
        raise ServerAlreadyExistsError(server_name)

    core = _find_core_jar(server_dir)
    java = _java_command(mc_version, root, core)

    start_batch = server_dir / paths.Files.START_BATCH
    write_start_batch(start_batch, server_dir, core, java,
                      get_config().RunningMemories_Min,
                      get_config().RunningMemories_Max,
                      nogui=get_config().Nogui)

    # 创建 eula.txt（直接同意）
    (server_dir / paths.Files.EULA).write_text("eula=true", encoding="utf-8")

    size = human_readable_size(directory_size(server_dir))
    server = ServerInstance(
        Name=server_name,
        Counts=0,
        Core=str(core),
        Path=str(server_dir),
        StartBatchPath=str(start_batch),
        Size=size,
        Version=mc_version,
        LatestStartedTime="N/A",
        CoreType=core_type,
    )
    if overwrite and registry.server_exists(server_name, root):
        # 覆盖时保留旧的启动统计
        old = registry.repair_server_info(server_name, root)
        server.Counts = old.Counts
        server.LatestStartedTime = old.LatestStartedTime
    server.save(root)
    logger.info("服务器已注册: %s (%s)", server_name, server_dir)
    return server


def create_server(server_name: str, core_type: str, mc_version: str,
                  root: Path | None = None) -> ServerInstance:
    """下载核心并创建新服务器（旧版 Processing.Build）。

    目录非空时自动追加 ``-repeat`` 后缀（保留旧版行为，但修复了
    ``-repeat-repeat`` 无限叠加的问题：先在全新名称上一次性确定）。
    """
    base_dir = paths.servers_dir(root)
    final_name, server_dir = _pick_free_server_dir(base_dir, server_name)

    core_file = core_downloader.download_core(final_name, core_type,
                                              mc_version, root)
    server = register_server(server_dir, final_name, mc_version,
                             core_type, overwrite=False, root=root)
    logger.info("服务器创建成功: %s", final_name)
    return server


def _pick_free_server_dir(base_dir: Path, name: str) -> tuple[str, Path]:
    """挑选一个空目录；目录非空时依次尝试 name-repeat、name-repeat-2 ..."""
    candidate, directory = name, base_dir / name
    suffix = 0
    while directory.exists() and any(directory.iterdir()):
        suffix += 1
        candidate = f"{name}-repeat" if suffix == 1 else f"{name}-repeat-{suffix}"
        directory = base_dir / candidate
    directory.mkdir(parents=True, exist_ok=True)
    return candidate, directory


def _find_core_jar(server_dir: Path) -> Path:
    """在服务器目录中定位核心 jar（旧版排除列表的合理化实现）。"""
    jars = [p for p in server_dir.rglob("*.jar")]
    if not jars:
        raise CoreFileNotFoundError(f"目录中没有 jar 文件: {server_dir}")
    if len(jars) == 1:
        return jars[0]

    def is_core(jar: Path) -> bool:
        lowered = str(jar).lower()
        return not any(kw in lowered for kw in _CORE_EXCLUDE_KEYWORDS)

    cores = [j for j in jars if is_core(j)]
    # 优先名字里带 server/minecraft/forge/fabric/mohist 的
    preferred = [j for j in cores
                 if any(kw in j.name.lower()
                        for kw in ("server", "minecraft", "forge",
                                   "fabric", "mohist", "paper", "spigot"))]
    chosen = (preferred or cores or jars)[0]
    logger.debug("选择核心文件: %s（共 %d 个 jar）", chosen, len(jars))
    return chosen


def _java_command(mc_version: str, root: Path | None,
                  core: Path | None = None) -> str:
    """返回带引号的 java 路径（提供 core 时按 jar 实测自动纠正）。

    找不到时退回 'java' 并告警（启动脚本仍可用 PATH 中的 java）。
    """
    try:
        if core is not None:
            java_path, _ = java_service.resolve_java_for_server(
                core, mc_version, root)
        else:
            java_path = resolve_java_for_minecraft(mc_version, root)
        return f'"{java_path}"'
    except Exception as exc:  # JavaNotFoundError 等，启动脚本仍用 PATH 中的 java
        logger.warning("未能定位 Java %s，启动脚本将使用 PATH 中的 java: %s",
                       mc_version, exc)
        return "java"


def write_start_batch(batch_path: Path, server_dir: Path, core: Path,
                      java: str, mem_min: int, mem_max: int,
                      nogui: bool = True) -> None:
    """生成 start.bat（与旧版格式兼容，Forge run.bat 转写逻辑保留）。"""
    lines = [f"cd {server_dir}"]
    run_bat = server_dir / paths.Files.FORGE_RUN_BATCH
    if run_bat.is_file():
        command = _extract_forge_run_command(run_bat, java, mem_min, mem_max)
        if command is None:
            command = f"{java} -Xms{mem_min}M -Xmx{mem_max}M -jar {core}"
        lines.append(command)
    else:
        lines.append(f"{java} -Xms{mem_min}M -Xmx{mem_max}M -jar {core}")
    if nogui:
        lines[-1] += " -nogui"
    lines.append("exit")
    batch_path.write_text("\n".join(lines), encoding="utf-8")
    logger.debug("启动脚本已生成: %s", batch_path)


def _extract_forge_run_command(run_bat: Path, java: str,
                               mem_min: int, mem_max: int) -> str | None:
    """从 Forge 的 run.bat 提取启动命令并替换 java 路径与内存参数。"""
    try:
        for line in run_bat.read_text(encoding="utf-8",
                                      errors="ignore").splitlines():
            if "--onlyCheckJava" in line:
                continue
            if "java" in line:
                command = line.strip().replace(
                    paths.Files.FORGE_JVM_ARGS,
                    f"-Xms{mem_min}M -Xmx{mem_max}M")
                # 只替换开头的 java 命令本身
                command = re.sub(r"^\S*java\S*", java, command, count=1)
                return command
    except OSError as exc:
        logger.error("读取 run.bat 失败: %s", exc)
    return None


# ------------------------------------------------------------ 启动 / 停止

def _build_launch_command(server: ServerInstance,
                          root: Path | None = None) -> list[str]:
    """构建服务器启动命令（直接 java 调用，不经过 cmd/start）。

    Java 路径经 :func:`java_service.resolve_java_for_server` 自动纠正：
    综合 MC 版本规则与 jar 内 class 文件版本实测，选择满足要求的 Java。
    """
    cfg = get_config()
    server_dir = Path(server.Path)
    core = _find_core_jar(server_dir)
    java_path, source = java_service.resolve_java_for_server(
        core, server.Version, root)
    logger.info("服务器 %s 使用 Java: %s（%s）", server.Name, java_path, source)

    memory = get_run_memory(server.Name, root)
    mem_min = memory["Xms"] or cfg.RunningMemories_Min
    mem_max = memory["Xmx"] or cfg.RunningMemories_Max
    run_bat = server_dir / paths.Files.FORGE_RUN_BATCH
    if run_bat.is_file():
        # Forge：沿用 run.bat 的参数结构（含 jvm args 文件），
        # 由 write_start_batch 转写到 start.bat，经 cmd 执行整树仍受 PID 管理
        write_start_batch(Path(server.StartBatchPath), server_dir, core,
                          java_path, mem_min, mem_max, cfg.Nogui)
        return ["cmd", "/c", server.StartBatchPath]

    # 同时刷新 start.bat 供用户手动使用（保持旧版文件兼容）
    write_start_batch(Path(server.StartBatchPath), server_dir, core,
                      java_path, mem_min, mem_max, cfg.Nogui)
    command = [java_path, f"-Xms{mem_min}M", f"-Xmx{mem_max}M",
               "-jar", str(core)]
    if cfg.Nogui:
        command.append("-nogui")
    return command


def _spawn(server: ServerInstance, root: Path | None = None):
    """以子进程启动服务器并登记 PID（生命周期由 process_manager 管理）。"""
    command = _build_launch_command(server, root)
    return process_manager.start(server.Name, command, cwd=server.Path)


def start_server(server_name: str, root: Path | None = None,
                 wait_rcon: bool = True,
                 rcon_timeout: int = 120) -> ServerInstance:
    """启动服务器（subprocess 进程管理版）。

    - 直接 java 调用（Forge 走 start.bat），不再依赖 cmd 窗口标题；
    - 首次启动：先跑一次让 Mojang 生成 eula.txt，同意后自动再启动；
    - RCON 等待循环有超时，不再死循环。
    """
    cfg = get_config()
    server = registry.repair_server_info(server_name, root)

    if process_manager.is_running(server.Name, server.Path):
        raise ServerRunningError(f"服务器已在运行: {server_name}")

    server.LatestStartedTime = detailed_time()

    # 首次启动：生成 eula → 同意 → 再正式启动
    if server.Counts == 0:
        logger.info("服务器 %s 首次启动，先生成 eula（最长 %d 秒）...",
                    server_name, cfg.WaitEulaGenerateTime)
        proc = _spawn(server, root)
        deadline = time.time() + cfg.WaitEulaGenerateTime
        while time.time() < deadline:
            if server.eula_file.is_file() or proc.poll() is not None:
                break
            time.sleep(1)
        # 确保预启动进程已退出再重新启动
        if proc.poll() is None:
            process_manager.stop(server.Name, server.Path)
        process_manager.wait_exit(server.Name, timeout=15)
        agree_eula(server)

    proc = _spawn(server, root)
    logger.info("服务器 %s 启动中（pid=%d）...", server_name, proc.pid)
    agree_eula(server)

    server.Counts += 1
    server.save(root)

    # 配置 RCON 并等待服务器就绪（有超时，不再死循环）
    if not rcon_service.is_rcon_enabled(server):
        try:
            rcon_service.setup_rcon(server)
        except (RconError, OSError) as exc:
            logger.warning("配置 RCON 失败: %s", exc)
    if wait_rcon and rcon_service.get_rcon_port(server) is not None:
        _wait_until_ready(server, rcon_timeout)

    _write_latest_files(server, root)
    logger.info("服务器 %s 启动完成，地址: 127.0.0.1:%s",
                server_name, _server_port(server))
    return server


def agree_eula(server: ServerInstance) -> None:
    """确保 eula.txt 同意协议（修复旧版 break 截断文件的 bug）。"""
    eula = server.eula_file
    if not eula.is_file():
        raise ServerError(f"eula.txt 不存在，服务器 {server.Name} 可能未正常启动")
    lines = eula.read_text(encoding="utf-8", errors="ignore").splitlines()
    new_lines = []
    found = False
    for line in lines:
        if line.strip().lower().startswith("eula="):
            new_lines.append("eula=true")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append("eula=true")
    eula.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def _wait_until_ready(server: ServerInstance, timeout: int) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if rcon_service.server_running(server):
            logger.info("服务器 %s 已就绪（RCON 可连接）", server.Name)
            return
        time.sleep(2)
    logger.warning("等待服务器 %s 就绪超时（%d 秒），继续执行",
                   server.Name, timeout)


def _server_port(server: ServerInstance) -> str:
    return properties.get_value(server.properties_file, "server-port") or "25565"


def _write_latest_files(server: ServerInstance, root: Path | None) -> None:
    """写 latest.txt（工作根）与 resource/latest.json（与旧版位置一致）。"""
    start_time = detailed_time()
    server.LatestStartedTime = start_time
    try:
        latest_txt = paths.workspace_root() if root is None else root
        (latest_txt / paths.Files.LATEST_TXT).write_text(
            f"服务器名称:{server.Name}\n{server.to_dict()}\n"
            f"服务器端口:{_server_port(server)}\n"
            f"启动时间:{start_time}",
            encoding="utf-8")
        latest_json = paths.resource_dir(root) / paths.Files.LATEST_JSON
        latest_json.write_text(
            json.dumps(server.to_dict(), indent=4, ensure_ascii=False),
            encoding="utf-8")
    except OSError as exc:
        logger.error("写入 latest 文件失败: %s", exc)


def stop_server(server_name: str, root: Path | None = None,
                grace_timeout: float = 20.0) -> None:
    """停止服务器：优先 RCON /stop 优雅停机，兜底按 PID 结束进程树。"""
    server = registry.repair_server_info(server_name, root)

    graceful_sent = False
    if rcon_service.is_rcon_enabled(server) \
            and rcon_service.server_running(server):
        try:
            rcon_service.execute_command(server, "stop")
            graceful_sent = True
            logger.info("已通过 RCON 发送 stop: %s", server_name)
        except RconError as exc:
            logger.warning("RCON stop 失败: %s", exc)

    if graceful_sent and process_manager.wait_exit(
            server.Name, timeout=grace_timeout):
        process_manager.stop(server.Name, server.Path)  # 清理登记与 PID 文件
        return

    if process_manager.is_running(server.Name, server.Path):
        if not process_manager.stop(server.Name, server.Path):
            raise ServerError(f"无法结束服务器进程: {server_name}")
    elif not graceful_sent:
        logger.warning("服务器 %s 未在运行", server_name)


def restart_server(server_name: str, root: Path | None = None) -> None:
    stop_server(server_name, root)
    start_server(server_name, root)


def is_server_running(server_name: str, root: Path | None = None) -> bool:
    """进程级状态查询（PID 存活或 RCON 可连）。"""
    try:
        server = registry.repair_server_info(server_name, root)
    except OmniArkError:
        return False
    if process_manager.is_running(server.Name, server.Path):
        return True
    return rcon_service.get_rcon_port(server) is not None \
        and rcon_service.server_running(server)


def start_latest(root: Path | None = None) -> ServerInstance:
    """启动最近一次启动过的服务器。"""
    latest_json = paths.resource_dir(root) / paths.Files.LATEST_JSON
    if not latest_json.is_file():
        raise ServerNotFoundError("（无最近启动记录）")
    data = json.loads(latest_json.read_text(encoding="utf-8"))
    name = data.get("Name")
    if not name:
        raise ServerNotFoundError("（latest.json 中没有 Name）")
    return start_server(name, root)


# ------------------------------------------------------------ 删除 / 修改

def delete_server(server_name: str, root: Path | None = None) -> None:
    """删除服务器（目录 + 注册信息）。二次确认由接口层负责。"""
    server = registry.repair_server_info(server_name, root)
    if server.exists():
        shutil.rmtree(server.directory)
        logger.info("服务器目录已删除: %s", server.Path)
    registry.remove_server_record(server_name, root)
    logger.info("服务器 %s 删除完成", server_name)


def rename_server(server_name: str, new_name: str,
                  root: Path | None = None) -> ServerInstance:
    """重命名服务器（仅改注册名，不动服务器目录）。"""
    if registry.server_exists(new_name, root):
        raise ServerAlreadyExistsError(new_name)
    server = registry.load_server(server_name, root)
    server.delete_save(root)
    server.Name = new_name
    server.save(root)
    logger.info("服务器 %s 已重命名为 %s", server_name, new_name)
    return server


def redirect_server_path(server_name: str, new_path: str | Path,
                         root: Path | None = None) -> ServerInstance:
    """重定向服务器目录（目录已由用户移动后，更新注册信息与启动脚本）。"""
    server = registry.load_server(server_name, root)
    new_dir = Path(new_path).resolve()
    old_path = server.Path

    server.Core = server.Core.replace(old_path, str(new_dir))
    server.StartBatchPath = server.StartBatchPath.replace(old_path, str(new_dir))
    server.Path = str(new_dir)
    server.save(root)

    # 重写启动脚本
    java = _java_command(server.Version, root, Path(server.Core))
    write_start_batch(Path(server.StartBatchPath), new_dir,
                      Path(server.Core), java,
                      get_config().RunningMemories_Min,
                      get_config().RunningMemories_Max,
                      nogui=get_config().Nogui)
    logger.info("服务器 %s 路径已重定向到 %s", server_name, new_dir)
    return server


def change_run_memory(server_name: str, mem_min: int, mem_max: int,
                      root: Path | None = None) -> None:
    """重写启动脚本中的内存参数。"""
    if mem_min > mem_max:
        mem_min, mem_max = mem_max, mem_min
    server = registry.repair_server_info(server_name, root)
    java = _java_command(server.Version, root, Path(server.Core))
    write_start_batch(Path(server.StartBatchPath), Path(server.Path),
                      Path(server.Core), java, mem_min, mem_max,
                      nogui=get_config().Nogui)
    logger.info("服务器 %s 内存已修改为 %dM-%dM", server_name, mem_min, mem_max)


def get_run_memory(server_name: str, root: Path | None = None) -> dict[str, int]:
    """从启动脚本解析 Xms/Xmx（脚本缺失时返回 0，调用方回退配置默认值）。"""
    server = registry.load_server(server_name, root)
    batch = Path(server.StartBatchPath)
    if not batch.is_file():
        return {"Xms": 0, "Xmx": 0}
    data = batch.read_text(encoding="utf-8", errors="ignore")
    xms = re.findall(r"-Xms(\d+)", data)
    xmx = re.findall(r"-Xmx(\d+)", data)
    return {"Xms": int(xms[0]) if xms else 0,
            "Xmx": int(xmx[0]) if xmx else 0}


def change_properties(server_name: str, values: dict[str, str],
                      root: Path | None = None) -> None:
    """批量修改 server.properties。"""
    server = registry.load_server(server_name, root)
    properties.set_values(server.properties_file, values)
    logger.info("服务器 %s 已更新 %d 项属性", server_name, len(values))


def open_mods_plugins(server_name: str, root: Path | None = None) -> None:
    """打开 mods/plugins 文件夹。"""
    server = registry.load_server(server_name, root)
    opened = False
    for folder in (server.mods_dir, server.plugins_dir):
        if folder.is_dir():
            process.open_in_explorer(folder)
            opened = True
    if not opened:
        raise ServerError("mods/plugins 文件夹不存在，请先启动一次服务器")


def get_terminal_logs(server_name: str, lines: int = 1000,
                      root: Path | None = None) -> str:
    """读取服务器 logs/latest.log 的最后 N 行。"""
    server = registry.load_server(server_name, root)
    log_file = server.directory / "logs" / paths.Files.LATEST_LOG
    if not log_file.is_file():
        raise ServerError(f"日志文件不存在: {log_file}")
    data = log_file.read_bytes()
    # 从尾部截取，避免读整个大文件
    text = data[-1024 * (lines + 1):].decode("utf-8", errors="ignore")
    return "\n".join(text.splitlines()[-lines:])