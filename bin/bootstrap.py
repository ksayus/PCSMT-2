import os
import sys

def get_base_path_inlet(relative_path=""):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.normpath(os.path.join(base_path, relative_path))

def run_bootstrap():
    base_path = get_base_path_inlet()
    os.chdir(base_path)

    # from bin.export import IsProgramRunning

    # import psutil
    # import sys

    # counts = IsProgramRunning.Is.Running()

    # import pygetwindow as gw

    # def SetWindowTop(window_title):
    #     windows = gw.getWindowsWithTitle(window_title)
    #     if windows:
    #         windows[0].activate()
    #         windows[0].bringToTop()
    #     else:
    #         print(f"未找到标题为 '{window_title}' 的窗口")

    # NowProgramPID = os.getpid()
    # ProgramName = psutil.Process(NowProgramPID).name()
    # if psutil.Process(NowProgramPID).name() == "python.exe":
    #     if counts > 1:
    #         SetWindowTop(ProgramName)
    #         sys.exit()
    # else:
    #     if counts > 2:
    #         SetWindowTop(ProgramName)
    #         sys.exit()

    import json
    from bin.export import Java
    from bin.export import Examine
    from bin.export import log

    java_versions_address = {
        "1.8": "",
        "16": "",
        "17": "",
        "21": ""
    }

    versions = [1.8, 16, 17, 21]
    for version in versions:
        results = Examine.Java.Exist(version)
        if results:
            for path, ver in results.items():
                log.logger.info(f"✅ 版本: {ver}已安装")
        else:
            log.logger.error(f"❌ 未安装版本{version}版本")
            log.logger.info('尝试安装Java...')
            log.logger.info(f'版本: {version}')
            try:
                result = Java.Install.Windows(version)
                if not result:
                    log.logger.error('Java安装失败')
                    log.logger.info(f'请手动安装Java {version}')
                else:
                    java_versions_address[f'{version}'] = version
            except Exception as e:
                log.logger.error(f'安装过程中发生异常: {str(e)}')

    try:
        with open('java_versions.json', 'r', encoding='utf-8') as f:
            java_versions_address = json.load(f)

            for javas in versions:
                if java_versions_address[f'{javas}'] == "":
                    log.logger.error(f'未检测到Java {javas}版本地址')
                    log.logger.info('自动获取Java版本地址...')
                    try:
                        jdks = os.listdir('C:\\Program Files\\Java')
                        for jdk in jdks:
                            if f'jdk{javas}' in jdk.lower():
                                log.logger.info(f'已获取Java {javas}版本地址：{jdk}')
                                java_versions_address[f'{javas}'] = f'C:\\Program Files\\Java\\{jdk}\\bin\\java.exe'
                                break
                    except  Exception as e:
                        log.logger.error(f'未找到 {javas}版本地址: {e}')
                        log.logger.info('正在安装Java...')
                        java_versions_address[f'{javas}'] = Java.Install.Windows(javas)

    except FileNotFoundError:
        log.logger.error('未找到java_versions.json文件，请检查文件是否存在！')
        log.logger.info('正在创建java_versions.json文件...')

    try:
        with open('java_versions.json', 'w', encoding='utf-8') as f:
            json.dump(java_versions_address, f, indent=4)
    except Exception as e:
        log.logger.error(f'保存java_versions.json文件时发生错误: {e}')
        log.logger.error(e)

    from bin.export import Info
    from bin.export import Init
    from bin.export import timer
    import threading

    timer.TimerStorageSizeUpdate.thread()

    Init.Infomation.Program()

    from bin.command import Program

    from bin.api import main

    Program.Do.CreateShortCut('PCSMT2-v' + Info.Config.PCSMT2_Version(), False)

    from bin.export import Key
    from bin.export import Admin

    Key.Generate.Key()

    if Admin.Examine.IsExistAdminAccount():
        pass
    else:
        log.logger.info('未检测到管理员账户文件，正在创建...')

        account_name = input("请输入管理员账号名称：")
        password = input("请输入管理员密码：")

        Admin.Set.AdminAccount(account_name, password)

    flask_thread = threading.Thread(target=main.run_flask, daemon=True)
    flask_thread.start()