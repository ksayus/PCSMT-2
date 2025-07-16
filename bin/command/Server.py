import os
import json
import time
import shutil
import zipfile
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import Info
from bin.export import Eula
from bin.export import log
from bin.export import Examine
from bin.export import IsProgramRunning
from bin.export import RCON
from bin.export import size_change
from bin.export import Get as GetThings
from packaging import version
from bin.export import timer
from bin.export import GetTime
from bin.command import Start
from bin.download import Core

class Processing:
    def Add(Path, server_name, rewrite, Version, CoreType):
        """
        添加服务器
        :param Path: 服务器路径
        :param server_name: 服务器名称
        :param rewrite: 是否覆盖同名服务器
        """
        # 获取绝对路径
        Path = os.path.abspath(Path)

        Core = find_file.find_files_with_extension(Path, '.jar')
        log.Debug(Path)
        log.Debug('找到服务器核心文件：' + str(Core))
        log.Debug('总共' + str(len(Core)) + '个文件')
        if len(Core) == 0:
            log.logger.error('未找到服务器核心文件，请检查文件路径是否正确！')
            return
        else:
            #若找到多个核心文件，排除server.jar文件,填入其他核心
            if len(Core) > 1:
                for i in range(len(Core)):
                    exclude_keywords = {
                        'server.jar',
                    }

                    Core = [
                        item for item in Core
                        if not any(keyword in item for keyword in exclude_keywords)
                    ]
                if len(Core) == 0:
                    log.logger.error('核心文件筛选后为空，请检查排除关键字设置！')
                    return
            if len(Core) == 0:
                log.logger.error('未找到有效的服务器核心文件！')
                return
            Core = Core[0]
            log.Debug('找到服务器核心文件：' + Core)
            if find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Save):
                find_file.find_files_with_existence_and_create(Path + Info.File.Document.StartBatch)

                AbsolutePath = Path + Info.File.Document.StartBatch
                os.path.abspath(AbsolutePath)
                log.Debug("找到服务器启动批处理文件,位置:" + AbsolutePath)

                try:
                    java_args: str = ''
                    v = version.parse(Version)
                    with open('./java_versions.json', 'r', encoding='utf-8') as f:
                        java_versions_address = json.load(f)

                        # 按照版本使用不同版本的Java JDK
                        # 获取Java版本
                        if v < version.parse('1.17.0'):
                            java_args = '"' f'{java_versions_address['1.8']}' '"'
                        elif v > version.parse('1.17.0') and v <= version.parse('1.18.2'):
                            java_args = '"' f'{java_versions_address['16']}' '"'
                        elif v > version.parse('1.18.2') and v <= version.parse('1.20.4'):
                            java_args = '"' f'{java_versions_address['17']}' '"'
                        elif v > version.parse('1.20.5') and v <= version.parse('1.21.7'):
                            java_args = '"' f'{java_versions_address['21']}' '"'

                    with open(Path + Info.File.Document.StartBatch, 'w') as f:
                        f.write('cd ' + Path + '\n')
                        if find_file.find_files_with_existence(Path + Info.File.Document.StartBatch):
                            try:
                                with open(Path + Info.File.Document.ForgeServerStartBatchDefaultName, 'r') as fi:
                                    log.Debug('发现run.bat文件,开始读取...')
                                    server_start_command = None
                                    for line in fi:
                                        # TODO: 处理新版 Forge 启动脚本: 跳过 java -jar forge-1.21.7-57.0.2-shim.jar --onlyCheckJava 语句
                                        if '--onlyCheckJava' in line:
                                            continue
                                        if 'java' in line:
                                            server_start_command = line.strip()
                                            break
                                    if server_start_command is None:
                                        log.logger.warning('未找到包含java的命令')
                                        log.logger.info('使用默认启动核心命令:')

                                        f.write(f'{java_args} -Xms' + str(Info.Config.RunningMemories_Min()) + 'M -Xmx' + str(Info.Config.RunningMemories_Max()) + 'M -jar ' + Core)
                                    else:
                                        StartCommand = ''
                                        log.Debug('读取服务器启动批处理文件成功!')
                                        StartCommand = server_start_command.replace(Info.File.Document.ForgeServer_JVM_args, '-Xms' + str(Info.Config.RunningMemories_Min()) + 'M -Xmx' + str(Info.Config.RunningMemories_Max()) + 'M').replace('java', java_args)
                                        log.Debug('服务器启动核心命令:' + StartCommand + '\n')
                                        f.write(StartCommand)
                            except Exception as e:
                                log.logger.error('服务器启动批处理文件读取失败!')
                                log.logger.error(e)
                                f.write(f'{java_args} -Xms' + str(Info.Config.RunningMemories_Min()) + 'M -Xmx' + str(Info.Config.RunningMemories_Max()) + 'M -jar ' + Core)
                        else:
                            f.write(f'{java_args} -Xms' + str(Info.Config.RunningMemories_Min()) + 'M -Xmx' + str(Info.Config.RunningMemories_Max()) + 'M -jar ' + Core)

                        if Info.Config.Nogui() == "true":
                            f.write(' -nogui')
                        else:
                            f.write('')
                        f.write('\n' + 'exit')
                        f.close()
                except Exception as e:
                    log.logger.error('创建服务器启动批处理文件失败!')
                    log.logger.error(e)
                    return

                # 创建eula.txt文件
                if find_file.find_files_with_existence_and_create(Path + Info.File.Document.Eula):
                    with open(Path + Info.File.Document.Eula, 'w') as f:
                        f.write('eula=true')

                if find_folder.find_folders_with_existence(Path):
                    server_size = size_change.size_change(GetThings.Info.DirSize(Path))

                if find_file.find_files_with_existence(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json'):
                    if rewrite == True:
                        log.logger.warning('已存在同名服务器，尝试覆盖原信息！')
                        try:
                            with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'r') as f:
                                server_info = json.load(f)
                                try:
                                    with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'w') as f:
                                        json.dump(server_info, f, indent=4)
                                        f.close()
                                except Exception as e:
                                    log.logger.error('创建服务器信息文件失败!')
                                    log.logger.error(e)
                                    return
                                f.close()
                                log.logger.info('覆盖服务器信息成功！')
                        except Exception as e:
                            log.logger.error('读取服务器信息文件失败!')
                            log.logger.error(e)
                            return
                    else:
                        log.logger.error('已存在同名服务器，请更换服务器名称！')
                        return
                else:
                    if find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json'):
                        start_count = 0
                        # Version = "0.0.0"
                        server_info = {
                            'Name': server_name,
                            'Counts': start_count,
                            'Core': Core,
                            'Path': Path,
                            'StartBatchPath': AbsolutePath,
                            'Size': server_size,
                            'Version': Version,
                            'LatestStartedTime': 'N/A',
                            'CoreType': CoreType
                            }
                        try:
                            with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'w') as f:
                                json.dump(server_info, f, indent=4)
                                f.close()
                            timer.TimerStorageSizeUpdate.thread()
                        except Exception as e:
                            log.logger.error('创建服务器信息文件失败!')
                            log.logger.error(e)
                            return
                    else:
                        log.logger.error('创建服务器信息文件失败!')

            Info.Information.ServerList.append(server_name)

    def Build(server_name, core_type, core_support_version):
        """
        创建服务器
        :param server_name: 服务器名称
        :param core_type: 核心类型
        :param core_support_version: 核心支持版本
        """
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            if find_folder.find_folders_with_existence(server_info['Path']):
                while(1):
                    all_files = find_file.find_files_with_extension(server_info['Path'], '')
                    if len(all_files) != 0:
                        log.logger.error('文件夹已有文件')
                        log.logger.info('为服务器文件夹添加 -repeat 字样')
                        server_info['Name'] += '-repeat'
                        server_info['Path'] = server_info['Path'].rstrip('\\') + '-repeat'
                        log.logger.debug(server_info)
                        if find_folder.find_folders_with_existence_and_create(server_info['Path']):
                            log.logger.info('创建文件夹:' + server_info['Path'])
                        else:
                            log.logger.error('创建文件夹失败！')
                            return
                    else:
                        break
            if Core.Processing.DownloadCore(server_name, core_type, core_support_version):
                log.logger.info('下载服务器核心成功！')
                log.logger.info('正在修改服务器信息文件...')
                Processing.Add(server_info['Path'], server_info['Name'], True, core_support_version, core_type)
                return
            else:
                log.logger.error('下载服务器核心失败！')
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            log.logger.warning('检测到服务器并未创建,创建服务器...')
            save_core_path = Info.work_path + Info.File.Folder.Servers + '/' + server_name
            find_folder.find_folders_with_existence_and_create(save_core_path)
            if Core.Processing.DownloadCore(server_name, core_type, core_support_version):
                log.logger.info('创建服务器成功！')
                log.logger.info('正在添加服务器...')
                Processing.Add(save_core_path, server_name, False, core_support_version, core_type)
                Info.Information.ServerList = Get.List()
                timer.TimerStorageSizeUpdate.thread()
            else:
                log.logger.error('创建服务器失败！')
                return
            return

    def Delete(server_name, double_check):
        """
        删除服务器
        :param server_name: 服务器名称
        :param double_check: 是否二次确认
        """
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            if server_info == False:
                log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                return
            else:
                log.logger.info('已找到服务器:' + server_info['Path'])
                if double_check:
                    try_count = 3
                    while try_count:
                        input_str = input('输入服务器名称以二次确认删除服务器:')
                        if input_str == server_name:
                            ensure_delete_server = True
                            while ensure_delete_server:
                                ensure = input('真的要删除服务器吗？这将会永久删除,无法恢复.(y/n)\n').strip().lower()

                                if ensure in ['y', 'yes']:
                                    try_count = 0
                                    break
                                elif ensure in ['n', 'no']:
                                    log.logger.info('已取消删除服务器！')
                                    return
                                else:
                                    log.logger.warning('输入错误，请输入 y 或 n！')
                        else:
                            log.logger.warning('服务器名称错误！')
                            try_count -= 1
                            log.logger.warning('您还有' + str(try_count) + '次机会！')
                            if try_count == 0:
                                log.logger.error('错误过多，删除服务器失败！')
                                return
                log.logger.info('正在删除服务器...')
                if find_folder.find_folders_with_existence(server_info['Path']):
                    # 删除服务器文件夹
                    shutil.rmtree(server_info['Path'])

                    log.logger.info('删除服务器成功！')
                    log.logger.info('正在删除服务器信息文件...')
                    os.remove(Info.work_path + Info.File.Folder.Save + '/' + server_name +'.json')
                log.logger.info('删除完成!')
                return
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return

    def Retracement(server_name: str, backup_file_name = None):
        """
        回档服务器
        :param server_name: 服务器名称
        """
        import stat

        def get_top_level_dirs(zip_path):
            top_dirs = set()  # 存储首级目录名称（自动去重）
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 遍历 ZIP 文件中的所有条目
                for name in zf.namelist():
                    # 提取首级目录（第一个路径部分）
                    first_part = name.split('/')[0]
                    # 判断是否为文件夹：
                    # 1. 条目以 "/" 结尾（显式目录），或
                    # 2. 首级目录下有子内容（隐式目录）
                    if name.endswith('/') or '/' in name:
                        top_dirs.add(first_part)
            # 过滤掉单独的文件名（无子内容的条目）
            return [d for d in top_dirs if any(
                entry.startswith(d + '/') or entry == d + '/'
                for entry in zf.namelist()
            )]

        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        if backup_file_name is None:
            log.logger.info('未指定回档文件名，将默认使用最新文件进行回档！')
            try:
                backups = Get.FindBackupFile(server_name)
                log.logger.info(f'尝试回档文件：{backups[-2]}')
                backup_file_name = backups[-2]

                # mod
                if backups[-1] == 'mod':
                    backup_file_content = Examine.Server.InfoKeys(server_name)
                    backup_file_absolute_path = backup_file_content['Path'] + '/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files = get_top_level_dirs(backup_file_absolute_path)
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['Path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['Path'] + '/' + file, arcname=backup_file_content['Path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['Path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['Path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['Path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}！')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['Path'])
                        log.logger.info('解压完成！')

                # plugin
                if backups[-1] == 'plugin':
                    backup_file_content = Examine.Server.InfoKeys(server_name)
                    backup_file_absolute_path = backup_file_content['Path'] + '/plugins/eBackup/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r')as zip_ref:
                        all_files = zip_ref.namelist()
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['Path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['Path'] + '/' + file, arcname=backup_file_content['Path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['Path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['Path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['Path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')
                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['Path'])
                        log.logger.info('解压完成！')
            except Exception as e:
                log.logger.error(f'解压文件失败!\n{e}')
                return False
        else:
            try:
                backups = Get.FindBackupFile(server_name)

                # mod
                if backups[-1] == 'mod':
                    backup_file_content = Examine.Server.InfoKeys(server_name)
                    backup_file_absolute_path = backup_file_content['Path'] + '/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files = get_top_level_dirs(backup_file_absolute_path)
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['Path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['Path'] + '/' + file, arcname=backup_file_content['Path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['Path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['Path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['Path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['Path'])
                        log.logger.info('解压完成！')
                # plugin
                if backups[-1] == 'plugin':
                    backup_file_content = Examine.Server.InfoKeys(server_name)
                    backup_file_absolute_path = backup_file_content['Path'] + '/plugins/eBackup/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files  = zip_ref.namelist()
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['Path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['Path'] + '/' + file, arcname=backup_file_content['Path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['Path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['Path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['Path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['Path'])
                        log.logger.info('解压完成！')
            except Exception as e:
                log.logger.error(f'解压文件失败!{e}')
                return False

class Do:
    class Ban:
        def Player(server_name, player_name):
            """
            封禁玩家
            :param server_name: 服务器名称
            :param player_name: 玩家名称
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/ban {player_name}')
                            log.logger.info(f'发送命令：ban {player_name}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

        def Ip(server_name, player_ip):
            """
            封禁玩家
            :param server_name: 服务器名称
            :param player_ip: IP地址
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/ban-ip {player_ip}')
                            log.logger.info(f'发送命令：ban-ip {player_ip}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

    class Unban:
        def Player(server_name, player_name):
            """
            解封玩家
            :param server_name: 服务器名称
            :param player_name: 玩家名称
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/pardon {player_name}')
                            log.logger.info(f'发送命令：pardon {player_name}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

        def Ip(server_name, player_ip):
            """
            解封玩家
            :param server_name: 服务器名称
            :param player_ip: IP地址
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/pardon-ip {player_ip}')
                            log.logger.info(f'发送命令：pardon-ip {player_ip}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

    class Set:
        def Op(server_name, player_name):
            """
            添加OP
            :param server_name: 服务器名称
            :param player_name: 玩家名称
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/op {player_name}')
                            log.logger.info(f'发送命令：op {player_name}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

        def Deop(server_name, player_name):
            """
            取消玩家操作权限
            :param server_name: 服务器名称
            :param player_name: 玩家名称
            """
            log.logger.info('查找服务器...')
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if server_info == False:
                    log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                    return
                else:
                    log.logger.info('已找到服务器:' + server_info['Path'])
                    port = RCON.Get.Port(server_info)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command(f'/deop {player_name}')
                            log.logger.info(f'发送命令：deop {player_name}')
                            log.logger.info(response)
                            server_command.disconnect()
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

    class Open:
        def Mods_Plugins_Folders(server_name):
            """
            打开服务器模组&插件文件夹
            :param server_name: 服务器名称
            """
            server_info = Examine.Server.InfoKeys(server_name)

            if find_folder.find_folders_with_existence(server_info['Path'] + Info.File.Folder.Mods) or find_folder.find_folders_with_existence(server_info['Path'] + Info.File.Folder.Plugins):
                try:
                    Start.Open.File(server_info['Path'] + Info.File.Folder.Mods)
                except Exception as e:
                    log.logger.error('打开服务器模组文件夹失败！')
                    log.logger.error(e)
                try:
                    Start.Open.File(server_info['Path'] + Info.File.Folder.Plugins)
                except Exception as e:
                    log.logger.error('打开服务器插件文件夹失败！')
                    log.logger.error(e)
            else:
                log.logger.error('服务器模组或插件文件夹不存在，请检查服务器是否启动过一次以上！')

    def Start(server_name):
        """
        启动服务器
        :param server_name: 服务器名称
        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json'):
            try:
                server_info = Examine.Server.InfoKeys(server_name)
                if not 'LatestStartedTime' in server_info:
                    server_info['LatestStartedTime'] = GetTime.TimeString.DetailedTime()
            except Exception as e:
                log.logger.error('读取服务器信息文件失败!')
                log.logger.error(e)
                return False

            try:
                Start.Open.File(server_info['StartBatchPath'])
            except Exception as e:
                log.logger.error('启动服务器失败！')
                log.logger.error(e)
                return False
            log.logger.info('启动服务器成功！')
            log.logger.info('当前启动服务器:' + server_name)
            time.sleep(2)
            if server_info['Counts'] == 0:
                log.logger.info("服务器第一次启动，请等待服务器启动完成！")
                time.sleep(int(Info.Config.WaitEulaGenerateTime()))
                if find_file.find_files_with_existence(server_info['Path'] + Info.File.Document.Eula):
                    log.logger.info('eula协议存在')
                    server_info = Eula.Examine.IsAgree(server_info)
                else:
                    log.logger.error('eula协议不存在, 服务器未正常启动, 请重新启动服务器！')
                    return False
            else:
                if server_info['Counts'] >= 1:
                    server_info = Eula.Examine.IsAgree(server_info)

            try:
                with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'w') as f:
                    server_info['Counts'] += 1
                    json.dump(server_info, f, indent=4)
                    f.close()
            except Exception as e:
                log.logger.error('修改服务器信息文件失败!')
                log.logger.error(e)
                return False

            try:
                # 获取端口
                with open(server_info['Path'] + Info.File.Document.ServerProperties, 'r', encoding='utf-8') as f:
                    log.logger.info('正在获取服务器端口...')
                    lines = f.readlines()
                    matched_lines = []
                    for line_number, line in enumerate(lines, start=1):
                        if 'server-port' in line:
                            matched_lines.append((line_number, line))
                            server_port = int(lines[line_number - 1].split('=')[1].strip())
            except Exception as e:
                log.logger.error('未找到服务器配置文件！')
                log.logger.error(e)
                return

            RCON_key = RCON.Infomation.EnableRCON(server_info)

            if RCON_key == 'false':
                port = 0
            else:
                #设置服务器rcon端口
                try:
                    port = None

                    if find_file.find_files_with_existence(server_info['Path'] + Info.File.Document.ServerProperties):
                        log.logger.debug('已找到server.properties文件！')
                        log.logger.info('正在设置rcon端口...')
                        port = RCON.Set.RCON(server_info)
                except Exception as e:
                    log.logger.error('设置rcon端口失败!')
                    log.logger.error(e)
                    return False

                ConnectStatus = False
                Port = RCON.Get.Port(server_info, msg=False)
                while not ConnectStatus:
                    try:
                        rcon = RCON.Get.RCON_Object(Port, msg=False)
                        rcon.connect()
                        rcon.disconnect()
                        time.sleep(2)
                        ConnectStatus = True
                    except Exception as e:
                        log.logger.error('连接RCON失败！')
                        log.logger.error(e)
                        # break
                        time.sleep(2) # 重试延迟

            # 输出latest文件
            try:
                StartTime = GetTime.TimeString.DetailedTime()
                if find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Document.Latest):
                    with open(Info.work_path + Info.File.Document.Latest, 'w', encoding='utf-8') as f:
                        f.write('服务器名称:' + server_name + '\n')
                        f.write(str(server_info) + '\n')
                        f.write('服务器端口:' + str(server_port) + '\n')
                        f.write('RCON端口:' + (str(port) if port else "未启用") + '\n')
                        f.write('启动时间:' + StartTime)
                        f.close()
                        log.logger.info('已输出latest.txt文件！')
                if find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json):
                    with open(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json, 'w', encoding='utf-8') as f:
                        json.dump(server_info, f, indent=4)
                        log.logger.info('已输出latest.json文件！')
            except Exception as e:
                log.logger.error('写入latest文件失败!')
                log.logger.error(e)

            log.logger.info('启动服务器成功！')
            log.logger.info('服务器端口号:' + str(server_port))
            log.logger.info('服务器本地连接地址:127.0.0.1:{0}'.format(server_port))
            return True
        else:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return False

    def Stop(server_name):
        """
        停止服务器
        :param server_name: 服务器名称
        """
        log.logger.info('查找服务器...')
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            RCON_key = RCON.Infomation.EnableRCON(server_info)
            if server_info == False:
                log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                return
            else:
                log.logger.info('已找到服务器:' + server_info['Path'])
                if RCON_key == 'false':
                    IsProgramRunning.Do.taskkill(server_name, 'cmd.exe')
                else:
                    port = RCON.Get.Port(server_info, msg=False)
                    if port != None:
                        try:
                            server_command = RCON.Get.RCON_Object(port, msg=False)
                            # 添加返回值类型检查
                            if not hasattr(server_command, 'connect'):
                                log.logger.error('获取RCON对象失败，无法连接')
                                return False
                        except Exception as e:
                            log.logger.error('链接rcon失败!')
                            log.logger.error(e)
                            return
                        time.sleep(1)
                        try:
                            server_command.connect()
                            response = server_command.command('/stop')
                            log.logger.info('发送命令：stop')
                            log.logger.info(response)
                            server_command.disconnect()
                            return True
                        except Exception as e:
                            log.logger.error('发送命令失败！')
                            log.logger.error(e)
                            return
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return

    def StartLatest():
        """
        启动上次启动的服务器
        """
        try:
            server_lists = find_file.find_files_with_existence(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json)
            if server_lists == False:
                log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                return False
            else:
                with open(Info.work_path + Info.File.Folder.Resource + Info.File.Document.Latest_json, 'r', encoding='utf-8') as f:
                    server_info = json.load(f)
                    f.close()
                log.logger.info('已找到服务器:' + server_info['Name'])
                log.logger.info('启动服务器...')
                inspection_server_started = Do.Start(server_info['Name'])
                if inspection_server_started == False:
                    log.logger.error('启动服务器失败！')
                else:
                    log.logger.info('启动服务器成功！')
                    return server_info
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return False

    def Restart(server_name):
        """
        重启服务器
        :param server_name: 服务器名称
        """
        try:
            log.logger.info('尝试重启服务器...')
            Do.Stop(server_name)
            time.sleep(3)
            Do.Start(server_name)
            log.logger.info('重启服务器成功！')
            return
        except Exception as e:
            log.logger.error('重启服务器失败！')
            log.logger.error(e)
            return

class Get:
    def List(ShowMessage = True):
        """
        列出服务器列表
        返回值：服务器列表(list)
        """
        server_list = find_file.find_files_with_extension(Info.work_path + Info.File.Folder.Save, '.json')
        if len(server_list) == 0:
            if ShowMessage:
                log.logger.error('未找到服务器，请添加服务器！')
            return
        else:
            server_lists = []
            if ShowMessage:
                log.logger.info('当前服务器列表：')
            for server in server_list:
                try:
                    # 检查文件是否为空
                    if os.path.getsize(server) == 0:
                        log.logger.error(f'服务器信息文件 {server} 为空，跳过该文件！')
                        continue

                    with open(server, 'r', encoding='utf-8') as f:
                        try:
                            server_info = json.load(f)
                        except json.JSONDecodeError as e:
                            # 捕获JSON解析错误并提供详细信息
                            log.logger.error(f'解析服务器信息文件 {server} 失败: {str(e)}')
                            log.logger.error('文件内容不是有效的JSON格式！')
                            continue

                        if 'Name' in server_info:
                            now_server_name = server_info['Name']
                        else:
                            log.Debug('服务器信息文件缺少Name字段！')
                            try:
                                with open(server, 'r', encoding='utf-8') as f:
                                    serverInfo = json.load(f)
                                server_info['Name'] = serverInfo['server_name']
                                with open(server, 'w', encoding='utf-8') as f:
                                    json.dump(server_info, f, ensure_ascii=False, indent=4)
                            except Exception as e:
                                log.logger.error('自动填充错误')
                                log.logger.error('将填充None信息')
                                log.logger.error(e)
                                server_info['Name'] = None
                        f.close()
                    if ShowMessage:
                        log.logger.info(now_server_name)
                    server_lists.append(now_server_name)
                except Exception as e:
                    log.logger.error(f'读取服务器信息文件 {server} 失败!')
                    log.logger.error(e)
                    continue
            if ShowMessage:
                log.logger.info('当前服务器数量：' + str(len(server_list)))
            return server_lists

    def Search(server_name, Output=True):
        """
        搜索服务器
        :param server_name: 服务器名称
        返回值：
        False(错误) or server_info(正确)
        """
        try:
            log.logger.debug('正在搜索服务器...')
            file_path = Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json'

            # 检查文件是否存在
            if not os.path.exists(file_path):
                log.logger.error(f'未找到服务器信息文件: {file_path}')
                return False

            # 检查文件是否为空
            if os.path.getsize(file_path) == 0:
                log.logger.error(f'服务器信息文件 {file_path} 为空！')
                return False

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        server_info = json.load(f)
                    except json.JSONDecodeError as e:
                        # 捕获JSON解析错误并提供详细信息
                        log.logger.error(f'解析服务器信息文件 {file_path} 失败: {str(e)}')
                        log.logger.error('文件内容不是有效的JSON格式！')
                        return False
            except Exception as e:
                log.logger.error('读取服务器信息文件失败！')
                log.logger.error(e)
                return

            if not 'Version' in server_info:
                server_info['Version'] = 'N/A'
            log.Debug('已找到服务器:' + server_info['Path'])
            log.Debug('已读取服务器信息文件...')
            # 当输出为False时，输出服务器信息
            # 输出服务器信息
            if Output:
                log.logger.info('服务器信息:')
                log.logger.info('服务器名称: ' + server_info['Name'])
                log.logger.info('服务器启动次数: ' + str(server_info['Counts']))
                log.logger.info('服务器核心: ' + server_info['Core'])
                log.logger.info('服务器路径: ' + server_info['Path'])
                log.logger.info('服务器启动批处理路径: ' + server_info['StartBatchPath'])
                log.logger.info('服务器大小: ' + str(server_info['Size']))
                log.logger.info('服务器核心版本: ' + str(server_info['Version']))
            return server_info
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return

    def FindBackupFile(server_name):
        """
        查找备份文件
        :param server_name: 服务器名称
        """
        keywords = [
            '.json'
        ]

        try:
            # 优先查找/mods/ftbbackups2
            # 文件名:ftbbackups2
            server_info = Examine.Server.InfoKeys(server_name)
            # mod
            if find_folder.find_folders_with_existence(server_info['Path'] + '/mods'):
                mod_list = os.listdir(server_info['Path'] + '/mods')
                for mods in mod_list:
                    if 'ftbbackups2' in mods:
                        log.logger.info('已找到FTB Backups 2 模组！')
                        log.logger.info('尝试获取备份列表...')
                        try:
                            log.logger.info('尝试获取FTB Backups 2 备份文件...')
                            backup_list = os.listdir(server_info['Path'] + '/backups')
                            # 按照时间排序
                            backup_list = sorted(backup_list, key=lambda x: os.path.getmtime(server_info['Path'] + '/backups/' + x))
                            if len(backup_list) > 0:
                                log.logger.info('已找到FTB Backups 2 备份文件！')

                                backups = [
                                    item for item in backup_list
                                    if not any(keyword in item for keyword in keywords)
                                ]

                                backups.append('mod')
                                return backups
                        except Exception as e:
                            log.logger.error('获取FTB Backups 2 备份文件失败！')
                            log.logger.error(e)
                            return
            # plugins
            if find_folder.find_folders_with_existence(server_info['Path'] + '/plugins'):
                plugin_list = os.listdir(server_info['Path'] + '/plugins')
                for plusins in plugin_list:
                    if 'ebackup' in plusins:
                        log.logger.info('已找到 eBackup 插件!')
                        log.logger.info('尝试获取备份列表...')
                        try:
                            log.logger.info('尝试获取 eBackup 备份文件...')
                            backup_list = os.listdir(server_info['Path'] + '/plugins/eBackup/backups')
                            if len(backup_list) > 0:
                                log.logger.info('已获取到 eBackup 备份文件...')

                                backups = [
                                    item for item in backup_list
                                    if not any(keyword in item for keyword in keywords)
                                ]

                                backups.append('plugin')
                                return backups
                        except Exception as e:
                            log.logger.error('获取 eBackup 备份文件失败!')
                            log.logger.error(e)
                            return
        except Exception as e:
            log.logger.error('获取服务器信息失败！')
            log.logger.error(e)
            return

class Change:
    def Properties(server_name, keyword, argument):
        """
        修改服务器属性
        :param server_name: 服务器名称
        :param keyword: 关键字
        :param argument: 参数
        """
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            find_file.find_keyword_inline_and_change_argument(server_info['Path'] + Info.File.Document.ServerProperties, keyword, argument)
        except Exception as e:
            log.logger.error('修改服务器属性失败！')
            log.logger.error(e)

    def RunningMemories(server_name, memory_min, memory_max):
        """
        修改服务器启动内存
        :param server_name: 服务器名称
        :param memory_min: 最小内存
        :param memory_max: 最大内存
        """
        server_info = Examine.Server.InfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
        else:
            try:
                with open(server_info['StartBatchPath'], 'w', encoding='utf-8') as f:
                    log.logger.info('正在修改服务器启动批处理文件...')
                    log.logger.info('修改服务器启动内存为：' + str(memory_min) + ' ' + str(memory_max))
                    f.write('cd ' + server_info['Path'] + '\n')
                    f.write('java -Xmx' + str(memory_min) + 'M -Xms' + str(memory_max) + 'M -jar ' + server_info['Core'])
                    if Info.Config.Nogui() == "true":
                        f.write(' -nogui')
                    else:
                        f.write('')
                    f.close()
                    log.logger.info('修改完毕！')
            except Exception as e:
                log.logger.error('读取服务器启动批处理文件失败！')
                log.logger.error(e)
                return

    def Rename(server_name, new_name):
        """
        重命名服务器
        :param server_name: 服务器名称
        :param new_name: 新服务器名称
        """
        log.logger.info('查找服务器...')
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            if server_info == False:
                log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            else:
                log.logger.info('已找到服务器:' + server_info['Path'])
                log.logger.info('重命名服务器...')
                try:
                    server_info['server_name'] = new_name
                    log.logger.info('重命名成功！')
                    log.logger.info('修改服务器信息文件...')
                    try:
                        with open(Info.work_path + Info.File.Folder.Save + '/' + new_name + '.json','w', encoding='utf-8') as f:
                            json.dump(server_info, f, indent=4)
                            f.close()
                            os.remove(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json')
                            log.logger.info('修改服务器信息文件成功！')
                    except Exception as e:
                        log.logger.error('修改服务器信息文件失败！')
                        log.logger.error(e)
                        return
                except Exception as e:
                    log.logger.error('重命名失败！')
                    log.logger.error(e)
                    return
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)

    def Redirected(server_name, new_path):
        """
        重定向服务器路径
        :param server_name: 服务器名称
        """
        log.logger.info('查找服务器...')
        try:
            server_info = Examine.Server.InfoKeys(server_name)
            if server_info == False:
                log.logger.error('未找到服务器，请检查服务器名称是否正确！')
                return
            else:
                log.logger.info('已找到服务器:' + server_info['Path'])
                log.logger.info('重定向服务器路径...')
                try:
                    log.logger.info('尝试重定向启动脚本和启动批处理文件...')
                    try:
                        server_info['Core'] = server_info['Core'].replace(server_info['Path'], new_path)
                        log.logger.info('重定向服务器核心成功！')
                        server_info['StartBatchPath'] = server_info['StartBatchPath'].replace(server_info['Path'], new_path)
                        log.logger.info('重定向服务器启动批处理文件成功！')
                        server_info['Path'] =   new_path
                        with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
                            json.dump(server_info, f, indent=4)
                        with open(server_info['StartBatchPath'], 'w') as f:
                            f.write('cd ' + server_info['Path'] + '\n')
                            f.write('java -Xms' + str(Info.Config.RunningMemories_Min()) + 'M -Xmx' + str(Info.Config.RunningMemories_Max()) + 'M -jar ' + server_info['Core'])
                            if Info.Config.Nogui() == 'true':
                                f.write(' -nogui\n')
                            else:
                                f.write('\n')
                            f.write('exit')
                        log.logger.info('覆写服务器启动批处理文件成功！')
                    except Exception as e:
                        log.logger.error('创建服务器启动批处理文件失败!')
                        log.logger.error(e)
                        log.logger.info('重定向服务器路径成功！')
                        log.logger.info('重定向成功！')
                except Exception as e:
                    log.logger.error('重定向失败！')
                    log.logger.error(e)
                    log.logger.info('修改服务器信息文件...')
                    try:
                        with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json','w', encoding='utf-8') as f:
                            json.dump(server_info, f, indent=4)
                            f.close()
                            log.logger.info('修改服务器信息文件成功！')
                    except Exception as e:
                        log.logger.error('修改服务器信息文件失败！')
                        log.logger.error(e)
                        return
                except Exception as e:
                    log.logger.error('重定向失败！')
                    log.logger.error(e)
                    return
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return