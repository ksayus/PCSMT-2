from bin.export import Is_program_running

Is_program_running.Is_program_running()

#检查Java是否安装
import sys
from bin.export import examin
from bin.export import log
from bin.command import program

java_exist = examin.examin_java_exist()
if java_exist:
    log.logger.info('Java已安装')
else:
    from bin.export import java
    log.logger.error('Java未安装')
    log.logger.info('自动安装Java...')

    versions = [8, 17, 21]
    installed = False

    for ver in versions:
        try:
            if java.install_java_windows(ver):
                installed = True
                break
            else:
                log.logger.error('Java安装失败')
                log.logger.info(f'请手动安装Java {ver}')
        except Exception as e:
            log.logger.error(f'安装过程中发生异常: {str(e)}')

    if not installed:
        log.logger.error('所有Java版本安装尝试均失败')


from bin.export import program_info
from bin.export import init

init.init_program()

from bin.introduction import introduction
from bin.command import start
from bin.command import server
from bin.export import numbers

from cmd2 import Cmd

from bin.api import server_api
import threading

program.Create_ShortCut('PCSMT2-v' + program_info.PCSMTVersion, False)

# server_api.app.run()
flask_thread = threading.Thread(target=server_api.run_flask, daemon=True)
flask_thread.start()


class PCSMT2(Cmd):
    intro = "欢迎使用PCSMT2"
    prompt = "PCSMT2>"

    # 版本号
    def do_version(self, arg):
        """查看版本号\nCommand: version"""
        introduction.Version()

    # 关于
    def do_about(self, arg):
        """查看介绍\nCommand: about"""
        introduction.Homepage()

    # 打开文件或目录
    def do_sta(self, file_path):
        """打开文件或目录\nCommand: sta <file_path>"""
        start.start_file(file_path)

    # 添加服务器
    def do_add_server(self, arg):
        """添加服务器\nCommand: add_server <server_path> <server_name>"""
        try:
            server_path, server_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.add_server(server_path, server_name, False)
    def complete_add_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return self.path_complete(text, line, begidx, endidx)
        elif arg_counts == 2:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 启动服务器
    def do_start_server(self, arg):
        """启动服务器\nCommand: start_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.start_server(server_name)
    def complete_start_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 查看服务器列表
    def do_server_list(self, arg):
        """查看服务器列表\nCommand: server_list"""
        server.server_list()

    # 修改服务器属性
    def do_change_server_properties(self, arg):
        """修改服务器属性\nCommand: change_server_properties <server_name> <keyword> <argument>"""
        try:
            server_name, keyword, argument = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.change_server_properties(server_name, keyword, argument)
    def complete_change_server_properties(self, text, line, begidx, endidx):
        """
        服务器属性自动补全函数（用于命令行自动补全功能）

        参数:
            text: str - 当前输入的补全文本
            line: str - 完整的命令行输入内容
            begidx: int - 补全起始位置
            endidx: int - 补全结束位置

        返回值:
            list - 包含匹配补全文本的建议值列表

        功能说明:
            根据输入参数数量提供不同层级的自动补全建议：
            - 第1参数补全服务器名称
            - 第2参数补全属性键
            - 第3参数补全特定属性值
        """
        # 解析输入参数（跳过命令本身）
        arg = line.split()[1:]
        arg_counts = len(arg)

        # 第1个参数：补全服务器名称
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

        # 第2个参数：补全属性键列表
        elif arg_counts == 2:
            return [list for list in program_info.properties_keyword if list.startswith(text)]

        # 第3个参数：根据属性键补全特定值
        elif arg_counts == 3:
            # 游戏模式补全值
            if arg[1] == "gamemode":
                gamemode = ["survival","creative","adventure","spectator"]
                return [list for list in gamemode if list.startswith(text)]

            # 难度级别补全值
            if arg[1] == "difficulty":
                difficulty = ["peaceful","easy","normal","hard"]
                return [list for list in difficulty if list.startswith(text)]

            # 布尔类型属性统一处理（true/false）
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

    # 修改服务器启动内存
    def do_change_server_run_memories_config(self, arg):
        """修改写入服务器启动脚本默认使用运行内存\nCommand: change_server_run_memories_config <memories_min> <memories_max>"""
        try:
            argument_min, argument_max = arg.split()
            #检查参数是否为数字
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
        program.change_server_run_memories_config(argument_min, argument_max)

    # 查看服务器插件列表
    def do_server_mods(self, arg):
        """查看服务器插件列表\nCommand: server_mods <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.open_server_mod_and_plugins_folder(server_name)
    def complete_server_mods(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 重写服务器启动脚本
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
        server.server_start_batch_rewrite_run_memories(server_name, memories_min, memories_max)
    def complete_server_start_batch_rewrite_run_memories(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 修改服务器启动nogui
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
        program.change_server_start_nogui(argument)
    def complete_change_server_start_nogui(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    # 下载服务器核心
    def do_download_server_core(self, arg):
        """下载服务器核心\nCommand: download_server_core <server_name> <core_type> <game_version>"""
        try:
            server_name, core_type, core_support_version = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.download_server_core(server_name, core_type, core_support_version)
    def complete_download_server_core(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 2:
            core_type = ['fabric', 'forge', 'official', 'mohist']
            return [list for list in core_type if list.startswith(text)]
        elif arg_count == 3:
            return [list for list in program_info.minecraft_version if list.startswith(text)]


    # 修改等待服务器eula生成时间
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
        program.change_wait_server_eula_generate_time(argument)

    # 删除服务器
    def do_delete_server(self, arg):
        """删除服务器\nCommand: delete_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.delete_server(server_name, True)
    def complete_delete_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 搜索服务器
    def do_search_server(self, arg):
        """搜索服务器\nCommand: search_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.search_server(server_name)
    def complete_search_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 封禁玩家或ip
    def do_banned(self, arg):
        """封禁玩家或ip\nCommand: banned <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            server.banned_ip(server_name, player_name_or_ip)
        if players_or_ips == "players":
            server.banned_player(server_name, player_name_or_ip)
    def complete_banned(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 解封玩家或ip
    def do_unban(self, arg):
        """解封玩家或ip\nCommand: unban <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            server.unban_ip(server_name, player_name_or_ip)
        elif players_or_ips == "players":
            server.unban_player(server_name, player_name_or_ip)
    def complete_unban(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 添加OP玩家
    def do_op(self, arg):
        """添加OP玩家\nCommand: op <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.op(server_name, player_name)
    def complete_op(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 删除OP玩家
    def do_deop(self, arg):
        """删除OP玩家\nCommand: deop <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.deop(server_name, player_name)
    def complete_deop(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 停止服务器
    def do_stop_server(self, arg):
        """停止服务器\nCommand: stop_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.stop_server(server_name)
    def complete_stop_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 修改服务器自启动
    def do_change_program_auto_startup(self, arg):
        """修改程序自动启动\nCommand: change_program_auto_startup <True / False>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        program.change_program_auto_startup(argument)
    def complete_change_program_auto_startup(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    # 重命名服务器
    def do_rename_server(self, arg):
        """重命名服务器\nCommand: rename_server <server_name> <new_name>"""
        try:
            server_name, new_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.rename_server(server_name, new_name)
    def complete_rename_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]

    # 重定向服务器路径
    def do_redirected_server_path(self, arg):
        """重定向服务器路径\nCommand: redirected_server_path <server_name> <new_path>"""
        try:
            server_name, new_path = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.redirected_server_path(server_name, new_path)
    def complete_redirected_server_path(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in program_info.server_list if list.startswith(text)]
        if arg_counts == 2:
            return self.path_complete(text, line, begidx, endidx)

    # 启动最新服务器
    def do_latest_started_server(self, arg):
        """启动最新服务器\nCommand: latest_started_server"""
        server.start_latest_server()

    # 输出程序信息
    def do_output_program_info(self, arg):
        """输出程序信息\nCommand: out_program_info"""
        program.output_program_info()

    # 格式化程序
    def do_format_program(self, arg):
        """格式化程序\nCommand: format_program"""
        program.format_program()

    # 清除缓存
    def do_clear_cache(self, arg):
        """清除缓存\nCommand: clear_cache"""
        program.clear_cache()

    # 退出控制台
    def do_exit(self, arg):
        """退出控制台\nCommand: exit"""
        log.logger.info("再见！")
        log.logger.info("欢迎再次使用PCSMT 2")
        return True  # 返回True会退出命令行循环

if __name__ == "__main__":
    console = PCSMT2()
    try:
        console.cmdloop()
    except KeyboardInterrupt:
        log.logger.info("\n退出PCSMT 2，正在安全关闭...")
        sys.exit(0)