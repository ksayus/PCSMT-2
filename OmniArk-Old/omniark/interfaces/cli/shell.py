"""OmniArk 交互式控制台（cmd2 实现）。

重构自旧版 ``bin/console/commands.py``（PCSMT2 类，34 个命令）。命令名保持
不变，后端全部改走 :mod:`omniark.services` 业务层 API，异常统一捕获
:class:`OmniArkError` 并输出中文提示，杜绝旧版 ``except Exception`` +
静默返回的模式。

相对旧版的修复：
- help 文本中的 ``Command:`` 与真实命令名不一致（build/output_program_info 等）
- 内存等数字参数使用字符串比较（"9" > "10"），这里统一转 int 再比较
- banned/unban 对非法类型参数静默无操作，这里给出明确错误
- do_change_storage_size_update_time / do_change_port 参数错误后仍继续执行
  （time/port 可能未定义），这里校验失败立即返回
- exit 直接 sys.exit(0)，这里返回 True 交给 cmd2 优雅退出
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from cmd2 import Cmd

from omniark.core.logger import get_logger
from omniark.exceptions import (
    BackupNotFoundError,
    DownloadError,
    OmniArkError,
    RconError,
    ServerAlreadyExistsError,
    ServerNotFoundError,
)
from omniark.interfaces.cli import introduction
from omniark.services import (
    backup_service,
    core_downloader,
    minecraft_versions,
    player_service,
    program_service,
    registry,
    server_service,
)
from omniark.utils import process

logger = get_logger()

# server.properties 常用键（Tab 补全候选）
PROPERTIES_KEYS: list[str] = [
    "gamemode", "difficulty", "pvp", "allow-flight", "spawn-protection",
    "spawn-npcs", "spawn-animals", "spawn-monsters", "online-mode",
    "white-list", "enable-command-block", "allow-nether", "force-gamemode",
    "hardcore", "max-players", "server-port", "view-distance", "motd",
    "level-name", "level-seed",
]

GAMEMODE_VALUES: list[str] = ["survival", "creative", "adventure", "spectator"]
DIFFICULTY_VALUES: list[str] = ["peaceful", "easy", "normal", "hard"]
BOOL_VALUES: list[str] = ["true", "false"]
# 取值为 true/false 的 properties 键
BOOL_PROPERTIES: dict[str, list[str]] = {
    "pvp": BOOL_VALUES,
    "allow-flight": BOOL_VALUES,
    "spawn-protection": BOOL_VALUES,
    "spawn-npcs": BOOL_VALUES,
    "spawn-animals": BOOL_VALUES,
    "spawn-monsters": BOOL_VALUES,
    "online-mode": BOOL_VALUES,
    "white-list": BOOL_VALUES,
    "enable-command-block": BOOL_VALUES,
    "allow-nether": BOOL_VALUES,
    "force-gamemode": BOOL_VALUES,
    "hardcore": BOOL_VALUES,
}

CORE_TYPES: list[str] = list(core_downloader.CORE_TYPES)
BAN_TYPES: list[str] = ["players", "ips"]
UPDATE_SOURCES: list[str] = ["github", "gitee"]


class OmniArkShell(Cmd):
    """OmniArk 命令行交互终端。"""

    intro = "欢迎使用 OmniArk（PCSMT-2 重构版），输入 help 查看全部命令"
    prompt = "OmniArk> "

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # 可注入的确认回调：(操作类型, 服务器名|None) -> bool。
        # GUI 等无 stdin 的界面应设置它（弹窗确认），CLI 下为 None 走 read_input。
        self.confirm_handler = None

    # ================================================================ 工具

    @staticmethod
    def _args_text(statement) -> str:
        """兼容 cmd2 Statement 对象与纯字符串，取参数文本。"""
        text = getattr(statement, "args", None)
        return text if text is not None else str(statement)

    def _split_args(self, statement) -> list[str]:
        return self._args_text(statement).split()

    def _parse_int(self, raw: str, label: str = "参数") -> int | None:
        """把字符串转成 int，失败时输出中文错误并返回 None。"""
        try:
            return int(raw)
        except ValueError:
            self.perror(f"参数错误：{label}必须是数字，收到: {raw!r}")
            return None

    def _parse_bool(self, raw: str) -> bool | None:
        """解析 true/false，失败时输出中文错误并返回 None。"""
        lowered = raw.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        self.perror(f"参数错误：请输入 true 或 false，收到: {raw!r}")
        return None

    def _normalize_memory(self, mem_min: int, mem_max: int) -> tuple[int, int]:
        """min > max 时交换并提示（修复旧版字符串比较 bug：先转 int 再比较）。"""
        if mem_min > mem_max:
            self.pwarning("参数警告：最小内存大于最大内存，已自动交换")
            return mem_max, mem_min
        return mem_min, mem_max

    # ------------------------------------------------------------ 补全数据源

    def _server_names(self) -> list[str]:
        """全部已注册服务器名，失败时返回空列表。"""
        try:
            return registry.list_server_names()
        except OmniArkError as exc:
            logger.debug("获取服务器列表失败: %s", exc)
            return []

    def _minecraft_versions(self) -> list[str]:
        """Minecraft 版本列表，网络失败时返回空列表。"""
        try:
            return minecraft_versions.fetch_minecraft_versions()
        except OmniArkError as exc:
            logger.debug("获取 Minecraft 版本列表失败: %s", exc)
            return []

    @staticmethod
    def _match(candidates: Iterable[str], text: str) -> list[str]:
        """前缀过滤补全候选，无匹配时返回空列表。"""
        return [item for item in candidates if item.startswith(text)]

    def _complete_server_names(self, text: str) -> list[str]:
        return self._match(self._server_names(), text)

    def _complete_mc_versions(self, text: str) -> list[str]:
        return self._match(self._minecraft_versions(), text)

    @staticmethod
    def _line_args(line: str) -> list[str]:
        """命令行中除命令名外的已输入参数。"""
        return line.split()[1:]

    # ================================================================ 信息

    def do_version(self, statement) -> None:
        """查看版本号
        Command: version"""
        introduction.print_version()

    def do_about(self, statement) -> None:
        """查看程序介绍
        Command: about"""
        introduction.print_homepage()

    # ================================================================ 系统

    def do_sta(self, statement) -> None:
        """打开文件或目录
        Command: sta <file_path>"""
        file_path = self._args_text(statement).strip()
        if not file_path:
            self.perror("参数错误：请输入要打开的文件或目录路径")
            return
        if not Path(file_path).exists():
            self.perror(f"路径不存在: {file_path}")
            return
        try:
            process.open_in_explorer(file_path)
            self.poutput(f"已打开: {file_path}")
        except OSError as exc:
            self.perror(f"打开文件失败: {exc}")

    # ================================================================ 服务器

    def do_add_server(self, statement) -> None:
        """添加（注册）已有服务器
        Command: add_server <server_path> <server_name> <server_version> <CoreType>"""
        args = self._split_args(statement)
        if len(args) != 4:
            self.perror("参数错误：add_server <server_path> <server_name> "
                        "<server_version> <CoreType>")
            return
        server_path, server_name, server_version, core_type = args
        try:
            server = server_service.register_server(
                server_path, server_name, server_version, core_type)
            self.poutput(f"服务器已注册: {server.Name} ({server.Path})")
        except ServerAlreadyExistsError as exc:
            self.perror(f"添加失败：{exc}")
        except OmniArkError as exc:
            self.perror(f"添加服务器失败: {exc}")

    def complete_add_server(self, text, line, begidx, endidx) -> list[str]:
        args = self._line_args(line)
        arg_count = len(args)
        if arg_count == 1:
            return self.path_complete(text, line, begidx, endidx)
        if arg_count == 2:
            return self._complete_server_names(text)
        if arg_count == 3:
            return self._complete_mc_versions(text)
        if arg_count == 4:
            return self._match(CORE_TYPES, text)
        return []

    def do_start_server(self, statement) -> None:
        """启动服务器
        Command: start_server <server_name>"""
        server_name = self._args_text(statement).strip()
        if not server_name:
            self.perror("参数错误：start_server <server_name>")
            return
        try:
            server_service.start_server(server_name)
            self.poutput(f"服务器 {server_name} 启动完成")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"启动服务器失败: {exc}")

    def complete_start_server(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_server_list(self, statement) -> None:
        """查看服务器列表
        Command: server_list"""
        names = self._server_names()
        if not names:
            self.poutput("当前没有已注册的服务器")
            return
        self.poutput(f"{'名称':<20}{'版本':<12}{'核心':<10}"
                     f"{'大小':<12}{'启动次数':<10}{'路径'}")
        self.poutput("-" * 80)
        for name in names:
            try:
                server = registry.repair_server_info(name)
            except OmniArkError as exc:
                self.pwarning(f"读取服务器 {name} 信息失败: {exc}")
                continue
            self.poutput(
                f"{server.Name:<20}{server.Version:<12}{server.CoreType:<10}"
                f"{server.Size:<12}{server.Counts:<10}{server.Path}")

    def do_change_server_properties(self, statement) -> None:
        """修改服务器属性（server.properties）
        Command: change_server_properties <server_name> <keyword> <argument>"""
        args = self._split_args(statement)
        if len(args) != 3:
            self.perror("参数错误：change_server_properties <server_name> "
                        "<keyword> <argument>")
            return
        server_name, keyword, argument = args
        try:
            server_service.change_properties(server_name, {keyword: argument})
            self.poutput(f"服务器 {server_name} 属性 {keyword} 已修改为 {argument}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"修改服务器属性失败: {exc}")

    def complete_change_server_properties(self, text, line, begidx,
                                          endidx) -> list[str]:
        args = self._line_args(line)
        arg_count = len(args)
        if arg_count == 1:
            return self._complete_server_names(text)
        if arg_count == 2:
            return self._match(PROPERTIES_KEYS, text)
        if arg_count == 3:
            keyword = args[1]
            if keyword == "gamemode":
                return self._match(GAMEMODE_VALUES, text)
            if keyword == "difficulty":
                return self._match(DIFFICULTY_VALUES, text)
            return self._match(BOOL_PROPERTIES.get(keyword, []), text)
        return []

    def do_change_server_run_memories_config(self, statement) -> None:
        """修改写入服务器启动脚本的默认运行内存（MB）
        Command: change_server_run_memories_config <memories_min> <memories_max>"""
        args = self._split_args(statement)
        if len(args) != 2:
            self.perror("参数错误：change_server_run_memories_config "
                        "<memories_min> <memories_max>")
            return
        mem_min = self._parse_int(args[0], "最小内存")
        mem_max = self._parse_int(args[1], "最大内存")
        if mem_min is None or mem_max is None:
            return
        mem_min, mem_max = self._normalize_memory(mem_min, mem_max)
        try:
            program_service.update_config(
                RunningMemories_Min=mem_min, RunningMemories_Max=mem_max)
            self.poutput(f"默认运行内存已修改为 {mem_min}M - {mem_max}M")
        except OmniArkError as exc:
            self.perror(f"修改默认运行内存失败: {exc}")

    def do_server_mods(self, statement) -> None:
        """打开服务器 mods/plugins 文件夹
        Command: server_mods <server_name>"""
        server_name = self._args_text(statement).strip()
        if not server_name:
            self.perror("参数错误：server_mods <server_name>")
            return
        try:
            server_service.open_mods_plugins(server_name)
            self.poutput(f"已打开服务器 {server_name} 的 mods/plugins 文件夹")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"打开 mods/plugins 文件夹失败: {exc}")

    def complete_server_mods(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_server_start_batch_rewrite_run_memories(self, statement) -> None:
        """重写服务器启动脚本的运行内存（MB）
        Command: server_start_batch_rewrite_run_memories <server_name> <memories_min> <memories_max>"""
        args = self._split_args(statement)
        if len(args) != 3:
            self.perror("参数错误：server_start_batch_rewrite_run_memories "
                        "<server_name> <memories_min> <memories_max>")
            return
        server_name = args[0]
        mem_min = self._parse_int(args[1], "最小内存")
        mem_max = self._parse_int(args[2], "最大内存")
        if mem_min is None or mem_max is None:
            return
        mem_min, mem_max = self._normalize_memory(mem_min, mem_max)
        try:
            server_service.change_run_memory(server_name, mem_min, mem_max)
            self.poutput(f"服务器 {server_name} 启动脚本内存已重写为 "
                         f"{mem_min}M - {mem_max}M")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"重写启动脚本失败: {exc}")

    def complete_server_start_batch_rewrite_run_memories(
            self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_change_server_start_nogui(self, statement) -> None:
        """修改服务器启动是否使用 nogui
        Command: change_server_start_nogui <true/false>"""
        value = self._parse_bool(self._args_text(statement).strip())
        if value is None:
            return
        try:
            program_service.update_config(Nogui=value)
            self.poutput(f"服务器启动 nogui 已修改为 {value}")
        except OmniArkError as exc:
            self.perror(f"修改 nogui 配置失败: {exc}")

    def complete_change_server_start_nogui(self, text, line, begidx,
                                           endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._match(BOOL_VALUES, text)
        return []

    def do_build(self, statement) -> None:
        """下载核心并创建服务器
        Command: build <server_name> <core_type> <game_version>"""
        args = self._split_args(statement)
        if len(args) != 3:
            self.perror("参数错误：build <server_name> <core_type> <game_version>")
            return
        server_name, core_type, mc_version = args
        try:
            server = server_service.create_server(server_name, core_type,
                                                  mc_version)
            self.poutput(f"服务器创建成功: {server.Name} ({server.Path})")
        except DownloadError as exc:
            self.perror(f"核心下载失败: {exc}")
        except OmniArkError as exc:
            self.perror(f"创建服务器失败: {exc}")

    def complete_build(self, text, line, begidx, endidx) -> list[str]:
        arg_count = len(self._line_args(line))
        if arg_count == 2:
            return self._match(CORE_TYPES, text)
        if arg_count == 3:
            return self._complete_mc_versions(text)
        return []

    def do_change_wait_server_eula_generate_time(self, statement) -> None:
        """修改等待服务器 eula 生成的时间（秒）
        Command: change_wait_server_eula_generate_time <time>"""
        raw = self._args_text(statement).strip()
        seconds = self._parse_int(raw, "等待时间")
        if seconds is None:
            return
        try:
            program_service.update_config(WaitEulaGenerateTime=seconds)
            self.poutput(f"等待 eula 生成时间已修改为 {seconds} 秒")
        except OmniArkError as exc:
            self.perror(f"修改等待时间失败: {exc}")

    def do_delete_server(self, statement) -> None:
        """删除服务器（需二次确认）
        Command: delete_server <server_name>"""
        server_name = self._args_text(statement).strip()
        if not server_name:
            self.perror("参数错误：delete_server <server_name>")
            return
        if not registry.server_exists(server_name):
            self.perror(f"服务器不存在: {server_name}")
            return
        if not self._confirm_delete(server_name):
            return
        try:
            server_service.delete_server(server_name)
            self.poutput(f"服务器 {server_name} 已删除")
        except OmniArkError as exc:
            self.perror(f"删除服务器失败: {exc}")

    def _confirm_delete(self, server_name: str) -> bool:
        """删除二次确认：输入服务器名 + y/n，共 3 次机会。"""
        if self.confirm_handler is not None:
            return bool(self.confirm_handler("delete_server", server_name))
        for attempt in range(3):
            remaining = 2 - attempt
            typed = self.read_input(
                f"请输入服务器名 [{server_name}] 以确认删除: ").strip()
            if typed != server_name:
                self.perror(f"名称不匹配，取消删除（剩余 {remaining} 次机会）")
                continue
            answer = self.read_input(
                "删除后不可恢复，确认删除？(y/n): ").strip().lower()
            if answer == "y":
                return True
            self.poutput("已取消删除")
            return False
        self.perror("3 次确认均失败，已取消删除")
        return False

    def complete_delete_server(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_search_server(self, statement) -> None:
        """按名称搜索服务器
        Command: search_server <server_name>"""
        keyword = self._args_text(statement).strip()
        if not keyword:
            self.perror("参数错误：search_server <server_name>")
            return
        matched = [name for name in self._server_names()
                   if keyword.lower() in name.lower()]
        if not matched:
            self.poutput(f"未找到名称包含 {keyword!r} 的服务器")
            return
        for name in matched:
            try:
                server = registry.repair_server_info(name)
            except OmniArkError as exc:
                self.pwarning(f"读取服务器 {name} 信息失败: {exc}")
                continue
            self.poutput(
                f"[{server.Name}] 版本={server.Version} 核心={server.CoreType} "
                f"大小={server.Size} 启动次数={server.Counts} "
                f"最近启动={server.LatestStartedTime} 路径={server.Path}")

    def complete_search_server(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    # ================================================================ 玩家

    def do_banned(self, statement) -> None:
        """封禁玩家或 IP
        Command: banned <players / ips> <server_name> <player_name / ip>"""
        args = self._split_args(statement)
        if len(args) != 3:
            self.perror("参数错误：banned <players / ips> <server_name> "
                        "<player_name / ip>")
            return
        ban_type, server_name, target = args
        try:
            if ban_type == "players":
                response = player_service.ban_player(server_name, target)
            elif ban_type == "ips":
                response = player_service.ban_ip(server_name, target)
            else:
                self.perror(f"参数错误：封禁类型必须是 players 或 ips，"
                            f"收到: {ban_type!r}")
                return
            self.poutput(f"封禁成功: {response}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except RconError as exc:
            self.perror(f"RCON 执行失败（服务器是否已启动？）: {exc}")
        except OmniArkError as exc:
            self.perror(f"封禁失败: {exc}")

    def complete_banned(self, text, line, begidx, endidx) -> list[str]:
        args = self._line_args(line)
        arg_count = len(args)
        if arg_count == 1:
            return self._match(BAN_TYPES, text)
        if arg_count == 2:
            return self._complete_server_names(text)
        return []

    def do_unban(self, statement) -> None:
        """解封玩家或 IP
        Command: unban <players / ips> <server_name> <player_name / ip>"""
        args = self._split_args(statement)
        if len(args) != 3:
            self.perror("参数错误：unban <players / ips> <server_name> "
                        "<player_name / ip>")
            return
        ban_type, server_name, target = args
        try:
            if ban_type == "players":
                response = player_service.unban_player(server_name, target)
            elif ban_type == "ips":
                response = player_service.unban_ip(server_name, target)
            else:
                self.perror(f"参数错误：解封类型必须是 players 或 ips，"
                            f"收到: {ban_type!r}")
                return
            self.poutput(f"解封成功: {response}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except RconError as exc:
            self.perror(f"RCON 执行失败（服务器是否已启动？）: {exc}")
        except OmniArkError as exc:
            self.perror(f"解封失败: {exc}")

    def complete_unban(self, text, line, begidx, endidx) -> list[str]:
        args = self._line_args(line)
        arg_count = len(args)
        if arg_count == 1:
            return self._match(BAN_TYPES, text)
        if arg_count == 2:
            return self._complete_server_names(text)
        return []

    def do_op(self, statement) -> None:
        """添加 OP 玩家
        Command: op <server_name> <player_name>"""
        args = self._split_args(statement)
        if len(args) != 2:
            self.perror("参数错误：op <server_name> <player_name>")
            return
        server_name, player_name = args
        try:
            response = player_service.op_player(server_name, player_name)
            self.poutput(f"已添加 OP: {response}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except RconError as exc:
            self.perror(f"RCON 执行失败（服务器是否已启动？）: {exc}")
        except OmniArkError as exc:
            self.perror(f"添加 OP 失败: {exc}")

    def complete_op(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_deop(self, statement) -> None:
        """移除 OP 玩家
        Command: deop <server_name> <player_name>"""
        args = self._split_args(statement)
        if len(args) != 2:
            self.perror("参数错误：deop <server_name> <player_name>")
            return
        server_name, player_name = args
        try:
            response = player_service.deop_player(server_name, player_name)
            self.poutput(f"已移除 OP: {response}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except RconError as exc:
            self.perror(f"RCON 执行失败（服务器是否已启动？）: {exc}")
        except OmniArkError as exc:
            self.perror(f"移除 OP 失败: {exc}")

    def complete_deop(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_stop_server(self, statement) -> None:
        """停止服务器
        Command: stop_server <server_name>"""
        server_name = self._args_text(statement).strip()
        if not server_name:
            self.perror("参数错误：stop_server <server_name>")
            return
        try:
            server_service.stop_server(server_name)
            self.poutput(f"服务器 {server_name} 已停止")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except RconError as exc:
            self.perror(f"RCON 执行失败（服务器是否已启动？）: {exc}")
        except OmniArkError as exc:
            self.perror(f"停止服务器失败: {exc}")

    def complete_stop_server(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    # ================================================================ 程序

    def do_change_program_auto_startup(self, statement) -> None:
        """修改程序是否开机自启
        Command: change_program_auto_startup <true / false>"""
        value = self._parse_bool(self._args_text(statement).strip())
        if value is None:
            return
        try:
            program_service.set_auto_startup(value)
            self.poutput(f"开机自启已{'开启' if value else '关闭'}")
        except OmniArkError as exc:
            self.perror(f"修改开机自启失败: {exc}")

    def complete_change_program_auto_startup(self, text, line, begidx,
                                             endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._match(BOOL_VALUES, text)
        return []

    def do_rename_server(self, statement) -> None:
        """重命名服务器
        Command: rename_server <server_name> <new_name>"""
        args = self._split_args(statement)
        if len(args) != 2:
            self.perror("参数错误：rename_server <server_name> <new_name>")
            return
        server_name, new_name = args
        try:
            server_service.rename_server(server_name, new_name)
            self.poutput(f"服务器 {server_name} 已重命名为 {new_name}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except ServerAlreadyExistsError as exc:
            self.perror(f"重命名失败：{exc}")
        except OmniArkError as exc:
            self.perror(f"重命名服务器失败: {exc}")

    def complete_rename_server(self, text, line, begidx, endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._complete_server_names(text)
        return []

    def do_redirected_server_path(self, statement) -> None:
        """重定向服务器路径
        Command: redirected_server_path <server_name> <new_path>"""
        args = self._split_args(statement)
        if len(args) != 2:
            self.perror("参数错误：redirected_server_path <server_name> <new_path>")
            return
        server_name, new_path = args
        try:
            server_service.redirect_server_path(server_name, new_path)
            self.poutput(f"服务器 {server_name} 路径已重定向到 {new_path}")
        except ServerNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"重定向服务器路径失败: {exc}")

    def complete_redirected_server_path(self, text, line, begidx,
                                        endidx) -> list[str]:
        arg_count = len(self._line_args(line))
        if arg_count == 1:
            return self._complete_server_names(text)
        if arg_count == 2:
            return self.path_complete(text, line, begidx, endidx)
        return []

    def do_latest_started_server(self, statement) -> None:
        """启动最近一次启动过的服务器
        Command: latest_started_server"""
        try:
            server = server_service.start_latest()
            self.poutput(f"最近启动的服务器 {server.Name} 已启动")
        except ServerNotFoundError as exc:
            self.perror(f"没有最近启动记录：{exc}")
        except OmniArkError as exc:
            self.perror(f"启动最近服务器失败: {exc}")

    def do_output_program_info(self, statement) -> None:
        """输出程序信息（版本与资源占用）
        Command: output_program_info"""
        info = program_service.program_info()
        cpu = program_service.cpu_usage()
        ram = program_service.ram_usage()
        disk = program_service.disk_usage()
        self.poutput("-------------------------------")
        self.poutput(f"程序名称: {info['name']}")
        self.poutput(f"程序版本: {info['version']}")
        self.poutput(f"Python 版本: {info['python']}")
        self.poutput(f"CPU 占用: {cpu['percent']}% "
                     f"({cpu['freq_current']}MHz / {cpu['freq_max']}MHz)")
        self.poutput(f"内存占用: {ram['percent']}% "
                     f"({ram['used_mb']}MB / {ram['total_mb']}MB)")
        self.poutput(f"磁盘占用: {disk['used_percent']}% "
                     f"(已用 {disk['used_gb']}GB / 共 {disk['total_gb']}GB)")
        self.poutput("-------------------------------")

    def do_format_program(self, statement) -> None:
        """格式化程序（清日志 + 清缓存 + 重置配置，服务器数据不动）
        Command: format_program"""
        if self.confirm_handler is not None:
            if not self.confirm_handler("format_program", None):
                self.poutput("已取消格式化")
                return
            answer = "y"
        else:
            answer = self.read_input(
                "将清空日志、缓存并重置配置（服务器数据不受影响），确认？(y/n): "
            ).strip().lower()
        if answer != "y":
            self.poutput("已取消格式化")
            return
        try:
            program_service.format_program()
            self.poutput("程序已格式化")
        except OmniArkError as exc:
            self.perror(f"格式化程序失败: {exc}")

    def do_clear_cache(self, statement) -> None:
        """清除缓存（非当日日志与 latest 文件）
        Command: clear_cache"""
        try:
            removed = program_service.clear_logs()
            program_service.clear_latest_files()
            self.poutput(f"缓存已清除（删除 {removed} 个旧日志目录）")
        except OmniArkError as exc:
            self.perror(f"清除缓存失败: {exc}")

    def do_reset_settings(self, statement) -> None:
        """重置设置为默认值
        Command: reset_settings"""
        try:
            program_service.reset_settings()
            self.poutput("设置已重置为默认值")
        except OmniArkError as exc:
            self.perror(f"重置设置失败: {exc}")

    def do_change_get_minecraft_test_version(self, statement) -> None:
        """修改是否获取 Minecraft 测试版（快照）版本
        Command: change_get_minecraft_test_version <true / false>"""
        value = self._parse_bool(self._args_text(statement).strip())
        if value is None:
            return
        try:
            program_service.update_config(MinecraftTestVersion=value)
            self.poutput(f"获取测试版版本已{'开启' if value else '关闭'}")
        except OmniArkError as exc:
            self.perror(f"修改配置失败: {exc}")

    def complete_change_get_minecraft_test_version(self, text, line, begidx,
                                                   endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._match(BOOL_VALUES, text)
        return []

    def do_retracement(self, statement) -> None:
        """回档服务器（不指定备份文件时使用最新备份）
        Command: retracement <server_name> [backup_file]"""
        args = self._split_args(statement)
        if not args:
            self.perror("参数错误：retracement <server_name> [backup_file]")
            return
        server_name = args[0]
        backup_file = args[1] if len(args) > 1 else None
        if backup_file in (None, "None"):
            backup_file = None
        if not registry.server_exists(server_name):
            self.perror(f"服务器不存在: {server_name}")
            return
        try:
            used = backup_service.restore_backup(server_name, backup_file)
            self.poutput(f"服务器 {server_name} 已从 {used.name} 回档完成")
        except BackupNotFoundError as exc:
            self.perror(str(exc))
        except OmniArkError as exc:
            self.perror(f"回档失败: {exc}")

    def complete_retracement(self, text, line, begidx, endidx) -> list[str]:
        args = self._line_args(line)
        arg_count = len(args)
        if arg_count == 1:
            return self._complete_server_names(text)
        if arg_count == 2:
            try:
                backups, _source = backup_service.find_backups(args[0])
            except OmniArkError:
                return []
            candidates = [item.name for item in backups] + ["None"]
            return self._match(candidates, text)
        return []

    def do_change_storage_size_update_time(self, statement) -> None:
        """修改服务器存储大小统计的更新间隔（秒）
        Command: change_storage_size_update_time <time>"""
        raw = self._args_text(statement).strip()
        seconds = self._parse_int(raw, "更新间隔")
        if seconds is None:
            return
        try:
            program_service.update_config(StorageSizeUpdateTime=seconds)
            self.poutput(f"存储大小更新间隔已修改为 {seconds} 秒")
        except OmniArkError as exc:
            self.perror(f"修改更新间隔失败: {exc}")

    def do_change_port(self, statement) -> None:
        """修改程序 API 服务端口
        Command: change_port <port>"""
        raw = self._args_text(statement).strip()
        port = self._parse_int(raw, "端口号")
        if port is None:
            return
        if not 1 <= port <= 65535:
            self.perror(f"参数错误：端口号必须在 1-65535 之间，收到: {port}")
            return
        try:
            program_service.update_config(Port=port)
            self.poutput(f"程序端口已修改为 {port}")
        except OmniArkError as exc:
            self.perror(f"修改端口失败: {exc}")

    def do_change_update_source(self, statement) -> None:
        """修改自动更新源
        Command: change_update_source <update_source>"""
        source = self._args_text(statement).strip().lower()
        if source not in UPDATE_SOURCES:
            self.perror(f"参数错误：更新源必须是 "
                        f"{' / '.join(UPDATE_SOURCES)}，收到: {source!r}")
            return
        try:
            program_service.update_config(AutoUpdateSource=source.capitalize())
            self.poutput(f"更新源已修改为 {source}")
        except OmniArkError as exc:
            self.perror(f"修改更新源失败: {exc}")

    def complete_change_update_source(self, text, line, begidx,
                                      endidx) -> list[str]:
        if len(self._line_args(line)) == 1:
            return self._match(UPDATE_SOURCES, text)
        return []

    # ================================================================ 退出

    def do_exit(self, statement) -> bool:
        """退出控制台
        Command: exit"""
        self.poutput("再见！欢迎再次使用 OmniArk")
        return True  # 交给 cmd2 优雅退出，不直接 sys.exit

    # ================================================================ help

    def complete_help(self, text, line, begidx, endidx) -> list[str]:
        all_commands = self.get_all_commands()
        return [cmd for cmd in all_commands if cmd.startswith(text)]
