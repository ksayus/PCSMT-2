import sys
from cmd2 import Cmd

from bin.introduction import introduction
from bin.command import Start
from bin.command import Server
from bin.command import Program
from bin.export import Info
from bin.export import log
from bin.export import numbers


class PCSMT2(Cmd):
    intro = "欢迎使用PCSMT2"
    prompt = "PCSMT2>"

    def do_version(self, arg):
        """查看版本号\nCommand: version"""
        introduction.Version()

    def do_about(self, arg):
        """查看介绍\nCommand: about"""
        introduction.Homepage()

    def do_sta(self, file_path):
        """打开文件或目录\nCommand: sta <file_path>"""
        Start.Open.File(file_path)

    def do_add_server(self, arg):
        """添加服务器\nCommand: add_server <server_path> <server_name> <server_version> <CoreType>"""
        try:
            server_path, server_name, server_version, CoreType = arg.split()
            print(server_path, server_name, server_version, CoreType)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Add(server_path, server_name, False, server_version, CoreType)

    def complete_add_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return self.path_complete(text, line, begidx, endidx)
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]
        elif arg_counts == 3:
            return [list for list in Info.Information.MinecraftVersion if list.startswith(text)]

    def do_start_server(self, arg):
        """启动服务器\nCommand: start_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Start(server_name)

    def complete_start_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_server_list(self, arg):
        """查看服务器列表\nCommand: server_list"""
        Server.Get.List()

    def do_change_server_properties(self, arg):
        """修改服务器属性\nCommand: change_server_properties <server_name> <keyword> <argument>"""
        try:
            server_name, keyword, argument = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Properties(server_name, keyword, argument)

    def complete_change_server_properties(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

        elif arg_counts == 2:
            return [list for list in Info.Information.PropertiesKeys if list.startswith(text)]

        elif arg_counts == 3:
            if arg[1] == "gamemode":
                gamemode = ["survival","creative","adventure","spectator"]
                return [list for list in gamemode if list.startswith(text)]

            if arg[1] == "difficulty":
                difficulty = ["peaceful","easy","normal","hard"]
                return [list for list in difficulty if list.startswith(text)]

            bool_properties = {
                "pvp": ["true","false"],
                "allow-flight": ["true","false"],
                "spawn-protection": ["true","false"],
                "spawn-npcs": ["true","false"],
                "spawn-animals": ["true","false"],
                "spawn-monsters": ["true","false"],
                "online-mode": ["true","false"]
            }
            return [val for val in bool_properties.get(arg[1], []) if val.startswith(text)]

    def do_change_server_run_memories_config(self, arg):
        """修改写入服务器启动脚本默认使用运行内存\nCommand: change_server_run_memories_config <memories_min> <memories_max>"""
        try:
            argument_min, argument_max = arg.split()
            if not argument_min.isdigit() or not argument_max.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
            if argument_min > argument_max:
                log.logger.warning('参数错误:最小内存不能大于最大内存')
                log.logger.info('已自动调整最小内存为最大内存')
                argument_max, argument_min = numbers.swap_numbers(argument_max, argument_min)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.RunningMemories_Config(argument_min, argument_max)

    def do_server_mods(self, arg):
        """查看服务器插件列表\nCommand: server_mods <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Open.Mods_Plugins_Folders(server_name)

    def complete_server_mods(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_server_start_batch_rewrite_run_memories(self, arg):
        """重写服务器启动脚本\nCommand: server_start_batch_rewrite_run_memories <server_name> <memories_min> <memories_max>"""
        try:
            server_name, memories_min, memories_max = arg.split()
            if not memories_min.isdigit() or not memories_max.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
            if memories_min > memories_max:
                log.logger.warning('参数错误:最小内存不能大于最大内存')
                log.logger.info('已自动调整最小内存为最大内存')
                memories_max, memories_min = numbers.swap_numbers(memories_max, memories_min)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.RunningMemories(server_name, memories_min, memories_max)

    def complete_server_start_batch_rewrite_run_memories(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_change_server_start_nogui(self, arg):
        """修改服务器启动nogui\nCommand: change_server_start_nogui <true/false>"""
        try:
            argument = arg.strip()
            if argument != "true" and argument != "false":
                log.logger.error('参数错误:请输入true或false')
                return
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.Nogui(argument)

    def complete_change_server_start_nogui(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    def do_build(self, arg):
        """下载服务器核心\nCommand: Build <server_name> <core_type> <game_version>"""
        try:
            server_name, core_type, core_support_version = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Build(server_name, core_type, core_support_version)

    def complete_build(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 2:
            core_type = ['fabric', 'forge', 'official', 'mohist']
            return [list for list in core_type if list.startswith(text)]
        elif arg_count == 3:
            return [list for list in Info.Information.MinecraftVersion if list.startswith(text)]

    def do_change_wait_server_eula_generate_time(self, arg):
        """修改等待服务器eula生成时间\nCommand: change_wait_server_eula_generate_time <time>"""
        try:
            argument = arg.strip()
            if not argument.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.WaitEulaGenerateTime(argument)

    def do_delete_server(self, arg):
        """删除服务器\nCommand: delete_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Delete(server_name, True)

    def complete_delete_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_search_server(self, arg):
        """搜索服务器\nCommand: search_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Get.Search(server_name)

    def complete_search_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_banned(self, arg):
        """封禁玩家或ip\nCommand: banned <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            Server.Do.Ban.Ip(server_name, player_name_or_ip)
        if players_or_ips == "players":
            Server.Do.Ban.Player(server_name, player_name_or_ip)

    def complete_banned(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_unban(self, arg):
        """解封玩家或ip\nCommand: unban <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            Server.Do.Unban.Ip(server_name, player_name_or_ip)
        elif players_or_ips == "players":
            Server.Do.Unban.Player(server_name, player_name_or_ip)

    def complete_unban(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_op(self, arg):
        """添加OP玩家\nCommand: op <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Set.Op(server_name, player_name)

    def complete_op(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_deop(self, arg):
        """删除OP玩家\nCommand: deop <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Set.Deop(server_name, player_name)

    def complete_deop(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_stop_server(self, arg):
        """停止服务器\nCommand: stop_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Stop(server_name)

    def complete_stop_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_change_program_auto_startup(self, arg):
        """修改程序自动启动\nCommand: change_program_auto_startup <True / False>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.AutoStartup(argument)

    def complete_change_program_auto_startup(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    def do_rename_server(self, arg):
        """重命名服务器\nCommand: rename_server <server_name> <new_name>"""
        try:
            server_name, new_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Rename(server_name, new_name)

    def complete_rename_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    def do_redirected_server_path(self, arg):
        """重定向服务器路径\nCommand: redirected_server_path <server_name> <new_path>"""
        try:
            server_name, new_path = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Redirected(server_name, new_path)

    def complete_redirected_server_path(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]
        if arg_counts == 2:
            return self.path_complete(text, line, begidx, endidx)

    def do_latest_started_server(self, arg):
        """启动最新服务器\nCommand: latest_started_server"""
        Server.Do.StartLatest()

    def do_output_program_info(self, arg):
        """输出程序信息\nCommand: out_program_info"""
        Program.Output.ProgramInfo()

    def do_format_program(self, arg):
        """格式化程序\nCommand: format_program"""
        Program.Format.Program()

    def do_clear_cache(self, arg):
        """清除缓存\nCommand: clear_cache"""
        Program.Format.Log()
        Program.Format.Latest()

    def do_reset_settings(self, arg):
        """重置设置\nCommand: reset_settings"""
        Program.Format.Settings()

    def do_change_get_minecraft_test_version(self, arg):
        """修改获取测试版服务器版本\nCommand: change_get_minecraft_test_version <True / False>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.MinecraftTestVersion(argument)

    def complete_change_get_minecraft_test_version(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    def do_retracement(self, arg):
        """回档服务器\nCommand: retracement [server_name]"""
        args = arg.strip().split(maxsplit=1)

        if not args or args[0] not in Info.Information.ServerList:
            log.logger.error(f"服务器不存在或参数错误: {args[0] if args else ''}")
            return

        server_name = args[0]
        backup_file = args[1] if len(args) > 1 else None

        Server.Processing.Retracement(server_name, backup_file)

    def complete_retracement(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [s for s in Info.Information.ServerList if s.startswith(text)]
        elif arg_counts == 2:
            backups = Server.Get.FindBackupFile(arg[0])
            backups.append('None')
            return [b for b in backups if b.startswith(text)]
        return []

    def do_change_storage_size_update_time(self, arg):
        try:
            time = arg.strip()
            if not time.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
        except ValueError as e:
            log.logger.error('参数错误，请输入正确的参数！')
            log.logger.error(e)
        Program.Change.StorageSizeUpdateTime(time)

    def do_change_port(self, arg):
        try:
            port = arg.strip()
            if not port.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
        except ValueError as e:
            log.logger.error('参数错误，请输入正确的参数！')
            log.logger.error(e)
        Program.Change.Port(int(port))

    def do_change_update_source(self, arg):
        """修改更新源\nCommand: change_update_source <update_source>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.UpdateSource(argument)

    def complete_change_update_source(self, text, line, begidx, endidx):
        update_sources = ['github', 'gitee']
        return [source for source in update_sources if source.startswith(text)]

    def do_exit(self, arg):
        """退出控制台\nCommand: exit"""
        log.logger.info("再见！")
        log.logger.info("欢迎再次使用PCSMT 2")
        sys.exit(0)
        return True

    def complete_help(self, text, line, begidx, endidx):
        all_commands = self.get_all_commands()
        return [cmd for cmd in all_commands if cmd.startswith(text)]