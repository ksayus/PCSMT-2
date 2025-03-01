import json
from bin.export import program_info
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log
from bin.export import init
from win32com.client import Dispatch
import sys
import os
import winreg
import winshell
import time
import atexit

def change_server_run_memories_config(argument_min, argument_max):
    """
    修改写入服务器启动脚本默认运行内存
    :param argument_min: 最小内存
    :param argument_max: 最大内存
    """
    """修改写入服务器启动脚本默认使用运行内存"""
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                server_info = json.load(f) # 读取json文件
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return
        server_info['default_server_run_memories_min'] = argument_min
        server_info['default_server_run_memories_max'] = argument_max
        try:
            with open(program_info.work_path + program_info.program_config, "w") as f:
                json.dump(server_info, f, indent=4) # 写入json文件
        except Exception as e:
            log.logger.error('写入程序配置文件失败！')
            log.logger.error(e)
            return
        log.logger.info("最小内存:" + server_info['default_server_run_memories_min'])
        log.logger.info("最大内存:" + server_info['default_server_run_memories_max'])
        log.logger.info("修改服务器启动内存成功")
    else:
        log.logger.error("程序配置文件不存在")
        return

def change_server_start_nogui(argument):
    """
    修改写入服务器启动脚本默认使用 nogui 启动
    :param argument: True/False
    """
    """修改写入服务器启动脚本默认使用 nogui 启动"""
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                config_read = json.load(f) # 读取json文件
                f.close()
            if(config_read['server_start_nogui'] == argument):
                log.logger.info('默认启用nogui状态已为:' + argument + '，无需修改')
                return
            else:
                config_read['server_start_nogui'] = argument
                try:
                    with open(program_info.work_path + program_info.program_config, "w") as f:
                        json.dump(config_read, f, indent=4) # 写入json文件
                        f.close()
                    log.logger.info("修改nogui设置成功")
                    program_info.server_start_nogui = argument
                except Exception as e:
                    log.logger.error('写入程序配置文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return

def change_wait_server_eula_generate_time(argument):
    """
    修改写入服务器启动脚本默认等待eula生成时间
    :param argument: 等待eula生成时间

    """
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                config_read = json.load(f) # 读取json文件
                f.close()
            if(config_read['wait_server_eula_generate_time'] == argument):
                log.logger.info('等待eula生成时间已为:' + argument + '，无需修改')
                return
            else:
                config_read['wait_server_eula_generate_time'] = argument
                try:
                    with open(program_info.work_path + program_info.program_config, "w") as f:
                        json.dump(config_read, f, indent=4) # 写入json文件
                        f.close()
                    log.logger.info("修改等待eula生成时间设置成功")
                    program_info.wait_server_eula_generate_time= argument
                except Exception as e:
                    log.logger.error('写入程序配置文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)

def change_server_run_memories_config(argument_min, argument_max):
    """
    修改写入服务器启动脚本默认运行内存
    :param argument_min: 最小内存
    :param argument_max: 最大内存
    """
    """修改写入服务器启动脚本默认使用运行内存"""
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                server_info = json.load(f) # 读取json文件
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return
        server_info['default_server_run_memories_min'] = argument_min
        server_info['default_server_run_memories_max'] = argument_max
        try:
            with open(program_info.work_path + program_info.program_config, "w") as f:
                json.dump(server_info, f, indent=4) # 写入json文件
        except Exception as e:
            log.logger.error('写入程序配置文件失败！')
            log.logger.error(e)
            return
        log.logger.info("最小内存:" + server_info['default_server_run_memories_min'])
        log.logger.info("最大内存:" + server_info['default_server_run_memories_max'])
        log.logger.info("修改服务器启动内存成功")
    else:
        log.logger.error("程序配置文件不存在")
        return

def change_server_start_nogui(argument):
    """
    修改写入服务器启动脚本默认使用 nogui 启动
    :param argument: True/False
    """
    """修改写入服务器启动脚本默认使用 nogui 启动"""
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                config_read = json.load(f) # 读取json文件
                f.close()
            if(config_read['server_start_nogui'] == argument):
                log.logger.info('默认启用nogui状态已为:' + argument + '，无需修改')
                return
            else:
                config_read['server_start_nogui'] = argument
                try:
                    with open(program_info.work_path + program_info.program_config, "w") as f:
                        json.dump(config_read, f, indent=4) # 写入json文件
                        f.close()
                    log.logger.info("修改nogui设置成功")
                    program_info.server_start_nogui = argument
                except Exception as e:
                    log.logger.error('写入程序配置文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return

def change_wait_server_eula_generate_time(argument):
    """
    修改写入服务器启动脚本默认等待eula生成时间
    :param argument: 等待eula生成时间

    """
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                config_read = json.load(f) # 读取json文件
                f.close()
            if(config_read['wait_server_eula_generate_time'] == argument):
                log.logger.info('等待eula生成时间已为:' + argument + '，无需修改')
                return
            else:
                config_read['wait_server_eula_generate_time'] = argument
                try:
                    with open(program_info.work_path + program_info.program_config, "w") as f:
                        json.dump(config_read, f, indent=4) # 写入json文件
                        f.close()
                    log.logger.info("修改等待eula生成时间设置成功")
                    program_info.wait_server_eula_generate_time= argument
                except Exception as e:
                    log.logger.error('写入程序配置文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return

def change_program_auto_startup(argument):
    """
    修改程序自动启动
    :param argument: True/False
    """
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        try:
            with open(program_info.work_path + program_info.program_config, "r") as f:
                config_read = json.load(f) # 读取json文件
                f.close()
            if(config_read['Automatic_startup'] == argument):
                log.logger.info('开机自启动已为:' + argument + '，无需修改')
                return
            else:
                config_read['Automatic_startup'] = argument
                try:
                    with open(program_info.work_path + program_info.program_config, "w") as f:
                        json.dump(config_read, f, indent=4) # 写入json文件
                        f.close()
                    log.logger.info("修改开机自启动设置成功")
                    program_info.wait_server_eula_generate_time= argument
                except Exception as e:
                    log.logger.error('写入程序配置文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('读取程序配置文件失败！')
            log.logger.error(e)
            return

def add_to_startup(name,file_path=""):
    """添加程序到自启动"""
	#By IvanHanloth
    if file_path == "":
        file_path = os.path.realpath(sys.argv[0])
    auth="IvanHanloth"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run",winreg.KEY_SET_VALUE, winreg.KEY_ALL_ACCESS|winreg.KEY_WRITE|winreg.KEY_CREATE_SUB_KEY)#By IvanHanloth
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
    winreg.CloseKey(key)
    log.logger.info("自动启动开启成功!")

def remove_from_startup(name):
    """
    取消程序自启动
    :param name: 程序名称
    """
    auth="IvanHanloth"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", winreg.KEY_SET_VALUE, winreg.KEY_ALL_ACCESS|winreg.KEY_WRITE|winreg.KEY_CREATE_SUB_KEY)#By IvanHanloth
    try:
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        print(f"{name} not found in startup.")
    else:
        print(f"{name} removed from startup.")
    winreg.CloseKey(key)

def Create_ShortCut(program_version, icon=True, description=True):
    """
    自动更新后创建快捷方式
    :param program_version: 程序版本
    """
    try:
        Desktop_Path = os.path.join(os.path.expanduser("~"), "Desktop")
        if find_file.find_files_with_existence(Desktop_Path + '/' + program_info.program_name + ".lnk") == False:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(os.path.join(winshell.desktop(), program_info.program_name + ".lnk"))
            shortcut.Targetpath = program_info.work_path + '/' + program_version + ".exe"
            #快捷方式起始位置
            shortcut.WorkingDirectory = os.path.dirname(program_info.work_path + '/' + program_version + ".exe")
            if icon:
                shortcut.IconLocation = program_info.work_path + '/' + program_version + ".exe"
            if description:
                shortcut.Description = "我的世界服务器管理终端"
            shortcut.save()
        else:
            log.logger.info('快捷方式已经存在')
        log.logger.info('创建快捷方式成功')
        return
    except Exception as e:
        log.logger.error('创建快捷方式失败！')
        log.logger.error(e)
        return

def Restart_Program(program_name):
    """
    自动更新结束后自动重启程序
    :param program_name: 程序名称
    """
    try:
        find_file.find_files_with_existence_and_create(program_info.work_path + program_info.delete_old_program)
        with open(program_info.work_path + program_info.delete_old_program, "w") as f:
            f.write("cd " + program_info.work_path + "\n")
            f.write("rm " + program_info.program_name + '-v' + program_info.PCSMTVersion + ".exe" + "\n")
            f.write("start " + program_name + ".exe" + "\n")
            f.write("exit")
            f.close()
        time.sleep(2)
        os.system("start " + program_info.work_path + program_info.delete_old_program)
        time.sleep(1)
        sys.exit()
    except Exception as e:
        log.logger.error('重启程序失败！')
        log.logger.error(e)
        return

def Delete_old_program():
    """删除程序自动更新时生成的脚本"""
    try:
        if find_file.find_files_with_existence(program_info.work_path + program_info.delete_old_program):
            os.remove(program_info.work_path + program_info.delete_old_program)
    except Exception as e:
        log.logger.error('删除旧脚本失败！')
        log.logger.error(e)
        return