from bin.export import log
from bin.export import program_info
from bin.introduction import introduction
from bin.command import start
from bin.command import server
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import numbers
from bin.command import program
from bin.export import init
from cmd import Cmd
import json
import sys

init.init_program()

class PCSMT2(Cmd):
    intro = "欢迎使用PCSMT2"
    prompt = "PCSMT2>"

    def do_version(self, arg):
        """查看版本号"""
        introduction.Version()

    def do_about(self, arg):
        """查看介绍"""
        introduction.Homepage()

    def do_sta(self, file_path):
        """打开文件或目录"""
        start.start_file(file_path)

    def do_add_server(self, arg):
        """添加服务器"""
        try:
            server_path, server_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.add_server(server_path, server_name, False)

    def do_start_server(self, arg):
        """启动服务器"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.start_server(server_name)

    def do_server_list(self, arg):
        """查看服务器列表"""
        server.server_list()

    def do_change_server_properties(self, arg):
        """修改服务器属性"""
        try:
            server_name, keyword, argument = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.change_server_properties(server_name, keyword, argument)

    def do_change_server_run_memories_config(self, arg):
        """修改写入服务器启动脚本默认使用运行内存"""
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

    def do_server_mods(self, arg):
        """查看服务器插件列表"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.open_server_mod_and_plugins_folder(server_name)

    def do_server_start_batch_rewrite_run_memories(self, arg):
        """重写服务器启动脚本"""
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

    def do_change_server_start_nogui(self, arg):
        """修改服务器启动nogui"""
        try:
            argument = arg.strip()
            if argument != "true" and argument != "false":
                log.logger.error('参数错误:请输入true或false')
                return
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        program.change_server_start_nogui(argument)

    def do_download_server_core(self, arg):
        """下载服务器核心"""
        try:
            server_name, core_type, core_support_version = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        server.download_server_core(server_name, core_type, core_support_version)

    def do_exit(self, arg):
        """退出控制台"""
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