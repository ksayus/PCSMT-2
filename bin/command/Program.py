import json
from bin.export import Info
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log
from win32com.client import Dispatch
from bin.export import GetTime
from bin.export import Get
from bin.export import timer
from time import sleep
import sys
import os
import winreg
import winshell
import time
import shutil
import threading

class Change:
    def RunningMemories_Config(argument_min, argument_max):
        """
        修改写入服务器启动脚本默认运行内存
        :param argument_min: 最小内存
        :param argument_max: 最大内存
        """
        """修改写入服务器启动脚本默认使用运行内存"""
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, "r") as f:
                    server_info = json.load(f) # 读取json文件
            except Exception as e:
                log.logger.error('读取程序配置文件失败！')
                log.logger.error(e)
                return
            server_info['RunningMemories_Min'] = argument_min
            server_info['RunningMemories_Max'] = argument_max
            try:
                with open(Info.work_path + Info.File.Document.Config, "w") as f:
                    json.dump(server_info, f, indent=4) # 写入json文件
            except Exception as e:
                log.logger.error('写入程序配置文件失败！')
                log.logger.error(e)
                return
            log.logger.info("最小内存:" + server_info['RunningMemories_Min'])
            log.logger.info("最大内存:" + server_info['RunningMemories_Max'])
            log.logger.info("修改服务器启动内存成功")
        else:
            log.logger.error("程序配置文件不存在")
            return

    def Nogui(argument):
        """
        修改写入服务器启动脚本默认使用 nogui 启动
        :param argument: True/False
        """
        """修改写入服务器启动脚本默认使用 nogui 启动"""
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, "r") as f:
                    config_read = json.load(f) # 读取json文件
                    f.close()
                if(config_read['Nogui'] == argument):
                    log.logger.info('默认启用nogui状态已为:' + argument + '，无需修改')
                    return
                else:
                    config_read['Nogui'] = argument
                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            json.dump(config_read, f, indent=4) # 写入json文件
                            f.close()
                        log.logger.info("修改nogui设置成功")
                        Info.Config.Nogui = argument
                    except Exception as e:
                        log.logger.error('写入程序配置文件失败！')
                        log.logger.error(e)
            except Exception as e:
                log.logger.error('读取程序配置文件失败！')
                log.logger.error(e)
                return

    def WaitEulaGenerateTime(argument):
        """
        修改写入服务器启动脚本默认等待eula生成时间
        :param argument: 等待eula生成时间

        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, "r") as f:
                    config_read = json.load(f) # 读取json文件
                    f.close()
                if(config_read['WaitEulaGenerateTime'] == argument):
                    log.logger.info('等待eula生成时间已为:' + argument + '，无需修改')
                    return
                else:
                    config_read['WaitEulaGenerateTime'] = argument
                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            json.dump(config_read, f, indent=4) # 写入json文件
                            f.close()
                        log.logger.info("修改等待eula生成时间设置成功")
                        Info.Config.WaitEulaGenerateTime= argument
                    except Exception as e:
                        log.logger.error('写入程序配置文件失败！')
                        log.logger.error(e)
            except Exception as e:
                log.logger.error('读取程序配置文件失败！')
                log.logger.error(e)

    def AutoStartup(argument):
        """
        修改程序自动启动
        :param argument: True/False
        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, "r") as f:
                    config_read = json.load(f) # 读取json文件
                    f.close()
                if(config_read['AutomaticStartup'] == argument):
                    log.logger.info('开机自启动已为:' + argument + '，无需修改')
                    return
                else:
                    config_read['AutomaticStartup'] = argument
                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            json.dump(config_read, f, indent=4) # 写入json文件
                            f.close()
                        log.logger.info("修改开机自启动设置成功")
                        Info.Config.AutomaticStartup= argument
                    except Exception as e:
                        log.logger.error('写入程序配置文件失败！')
                        log.logger.error(e)
            except Exception as e:
                log.logger.error('读取程序配置文件失败！')
                log.logger.error(e)
                return

    def MinecraftTestVersion(argument):
        """
        修改获取测试版服务器版本
        :param argument: True/False
        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, 'r', encoding='utf-8') as f:
                    config_read = json.load(f)
                    f.close()
                if config_read['MinecraftTestVersion'] == argument:
                    log.logger.info(f'开关状态已为{argument},无需修改')
                    return
                else:
                    config_read['MinecraftTestVersion'] = argument
                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            f.write(json.dumps(config_read, indent=4))
                            f.close()
                        log.logger.info('修改获取测试版服务器版本开关成功！')
                        Info.Config.MinecraftTestVersion = argument
                    except Exception as e:
                        log.logger.error('写入config文件失败')
                        log.logger.error(e)
                        return
                Info.Information.MinecraftVersion = Get.Info.MinecraftVersion()
            except Exception as e:
                log.logger.error('读取config文件失败！')
                log.logger.error(e)
                return

    def StorageSizeUpdateTime(time):
        """
        更改存储大小更新时间
        参数：
        time -> int 存储空间更新时间
        单位 ：秒
        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            try:
                with open(Info.work_path + Info.File.Document.Config, "r") as f:
                    config_read = json.load(f) # 读取json文件
                if(config_read['StorageSizeUpdateTime'] == int(time)):
                    log.logger.info('更改存储大小更新时间已为:' + time + '，无需修改')
                    return
                else:
                    config_read['StorageSizeUpdateTime'] = int(time)
                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            json.dump(config_read, f, indent=4) # 写入json文件
                        log.logger.info("修改更改存储大小更新时间设置成功")
                        # 先关闭当前线程
                        for thread in threading.enumerate():
                            log.Debug(thread.name)
                            if 'start_timer' in thread.name:
                                if thread.is_alive(): # 判断线程是否存活
                                    timer.TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.set()
                                    thread.join()
                                    # log.logger.info(f'已取消{thread.name}服务器存储空间更新任务！')

                        # 然后再次启动以应用修改
                        sleep(1)
                        timer.TimerStorageSizeUpdate.thread()
                        log.Debug('已启动服务器存储空间更新任务！')
                    except Exception as e:
                        log.logger.error('写入程序配置文件失败！')
                        log.logger.error(e)
            except Exception as e:
                log.logger.error('读取程序配置文件失败！')
                log.logger.error(e)
                return

class Do:

    def AddStartup(name,file_path=""):
        """添加程序到自启动"""
        #By IvanHanloth
        if file_path == "":
            file_path = os.path.realpath(sys.argv[0])
        auth="IvanHanloth"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run",winreg.KEY_SET_VALUE, winreg.KEY_ALL_ACCESS|winreg.KEY_WRITE|winreg.KEY_CREATE_SUB_KEY)#By IvanHanloth
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        log.logger.info("自动启动开启成功!")

    def RemoveStartup(name):
        """
        取消程序自启动
        :param name: 程序名称
        """
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", winreg.KEY_SET_VALUE, winreg.KEY_ALL_ACCESS|winreg.KEY_WRITE|winreg.KEY_CREATE_SUB_KEY)#By IvanHanloth
        try:
            winreg.DeleteValue(key, name)
        except FileNotFoundError:
            print(f"{name} not found in startup.")
        else:
            print(f"{name} removed from startup.")
        winreg.CloseKey(key)

    def ShortCut(program_version,icon=True,description=True):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(os.path.join(winshell.desktop(), Info.program_name + ".lnk"))
        shortcut.Targetpath = Info.work_path + '/' + program_version + ".exe"
        #快捷方式起始位置
        shortcut.WorkingDirectory = os.path.dirname(Info.work_path + '/' + program_version + ".exe")
        if icon:
            shortcut.IconLocation = Info.work_path + '/' + program_version + ".exe"
        if description:
            shortcut.Description = "我的世界服务器管理终端"
        shortcut.save()

    def CreateShortCut(program_version, recoverage):
        """
        自动更新后创建快捷方式
        :param program_version: 程序版本
        """
        try:
            Desktop_Path = os.path.join(os.path.expanduser("~"), "Desktop")
            if recoverage:
                Do.ShortCut(program_version)
            else:
                if find_file.find_files_with_existence(Desktop_Path + '/' + Info.program_name + ".lnk") == False:
                    Do.ShortCut(program_version)
                else:
                    log.logger.info('快捷方式已经存在')
                    return
            log.logger.info('创建快捷方式成功')
            return
        except Exception as e:
            log.logger.error('创建快捷方式失败！')
            log.logger.error(e)
            return

class Processing:
    def Restart(program_name):
        """
        自动更新结束后自动重启程序
        :param program_name: 程序名称
        """
        try:
            find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Document.DeteleteOldProgram)
            with open(Info.work_path + Info.File.Document.DeteleteOldProgram, "w") as f:
                f.write(
                    "@echo off\n"
                    "if \"%1\" == \"h\" goto begin\n"
                    "start mshta vbscript:createobject(\"wscript.shell\").run(\"\"\"%~nx0\"\"h\",0)(window.close)&&exit\n"
                    ":begin\n"
                    "timeout /t 5\n"
                    "cd " + Info.work_path + "\n"
                    "powershell rm " + Info.work_path + '/' + Info.program_name + '-v' + Info.Config.PCSMT2_Version + ".exe" + "\n"
                    "start " + program_name + ".exe" + "\n"
                    "exit"
                )
                f.close()
            time.sleep(2)
            os.system("start " + Info.work_path + Info.File.Document.DeteleteOldProgram + " h")
            time.sleep(1)
            sys.exit()
        except Exception as e:
            log.logger.error('重启程序失败！')
            log.logger.error(e)
            return

    def Delete_Script():
        """删除程序自动更新时生成的脚本"""
        try:
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.DeteleteOldProgram):
                os.remove(Info.work_path + Info.File.Document.DeteleteOldProgram)
        except Exception as e:
            log.logger.error('删除旧脚本失败！')
            log.logger.error(e)
            return

class Output:
    def ProgramInfo():
        """输出程序信息"""
        try:
            log.logger.info('程序名称: ' + Info.program_name)
            log.logger.info(Info.Config.ConfigRead)
        except Exception as e:
            log.logger.error('输出程序信息失败！')
            log.logger.error(e)
            return

class Format:
    def Log():
        """删除日志"""
        try:
            if find_folder.find_folders_with_existence(Info.work_path + Info.File.Folder.Logs):
                all_folders = os.listdir(Info.work_path + Info.File.Folder.Logs)
                log.logger.debug(all_folders)
                try:
                    for folder in all_folders:
                        # 获取月份文件夹
                        all_folders_years_months = os.listdir(Info.work_path + Info.File.Folder.Logs + '/' + folder)
                        log.logger.debug(all_folders_years_months)
                        for all__folders_year_month in all_folders_years_months:
                            # 获取日期文件夹
                            all_folders_years_months_days = os.listdir(Info.work_path + Info.File.Folder.Logs + '/' + folder + '/' + all__folders_year_month)
                            log.logger.debug(all_folders_years_months_days)
                            for all_folders_year_month_day in all_folders_years_months_days:
                                # 获取日志文件
                                all_folders_years_months_days_logs = os.listdir(Info.work_path + Info.File.Folder.Logs + '/' + folder + '/' + all__folders_year_month + '/' + all_folders_year_month_day)
                                log.logger.debug(all_folders_years_months_days_logs)
                                for all_folders_year_month_day_log in all_folders_years_months_days_logs:
                                    if all_folders_year_month_day_log != f"{log.now_time}.log":
                                        os.remove(Info.work_path + Info.File.Folder.Logs + '/' + folder + '/' + all__folders_year_month + '/' + all_folders_year_month_day + '/' + all_folders_year_month_day_log)
                                        log.logger.info(f'删除日志文件: {all_folders_year_month_day_log}')

                                if all_folders_year_month_day != str(GetTime.Time.Day):
                                    shutil.rmtree(Info.work_path + Info.File.Folder.Logs + '/' + folder + '/' + all__folders_year_month + '/' + all_folders_year_month_day)
                            if all__folders_year_month != str(GetTime.Time.Month):
                                shutil.rmtree(Info.work_path + Info.File.Folder.Logs + '/' + folder + '/' + all__folders_year_month)
                        if folder != str(GetTime.Time.Year):
                            shutil.rmtree(Info.work_path + Info.File.Folder.Logs + '/' + folder)
                except Exception as e:
                    log.logger.error('删除日志文件失败！')
                    log.logger.error(e)
        except Exception as e:
            log.logger.error('删除日志文件夹失败！')
            log.logger.error(e)
            return

    def Settings():
        """重置设置"""
        try:
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
                with open(Info.work_path + Info.File.Document.Config, "w") as f:
                    json.dump(Info.Config.Config, f, indent=4)
                    f.close()
        except Exception as e:
            log.logger.error('重置设置失败！')
            log.logger.error(e)
            return

    def Server():
        """移除服务器"""
        try:
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
                with open(Info.work_path + Info.File.Document.Config, "w") as f:
                    json.dump(Info.Config.Config, f, indent=4)
                    f.close()
        except Exception as e:
            log.logger.error('移除服务器失败！')
            log.logger.error(e)
            return

    def Latest():
        """清除最新启动的服务器"""
        try:
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Latest):
                with open(Info.work_path + Info.File.Document.Latest, "w") as f:
                    f.write("")
                    f.close()
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Latest_json):
                with open(Info.work_path + Info.File.Document.Latest_json, "w") as f:
                    f.write("")
                    f.close()
        except Exception as e:
            log.logger.error('清除最新启动的服务器失败！')
            log.logger.error(e)
            return

    def Program():
        """格式化程序"""
        ensure = input('是否格式化程序?(y/n): ')
        if ensure.lower() in {'y', 'yes'}:
            log.logger.info('格式化程序中...')
        else:
            log.logger.info('格式化程序取消！')
            return False

        try:
            Format.Log()
            Format.Server()
            Format.Latest()
            Format.Settings()
        except Exception as e:
            log.logger.error('格式化程序失败！')
            log.logger.error(e)
            return