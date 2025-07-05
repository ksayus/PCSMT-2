import os
import json
import time
import shutil
import zipfile
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import program_info
from bin.command import start
from bin.export import eula
from bin.export import log
from bin.export import examin
from bin.download import server_core
from bin.export import rcon
from bin.export import size_change
from bin.export import get
from packaging import version
from bin.export import timer
from bin.export import get_time
def add_server(server_path, server_name, rewrite, server_version):
    """
    添加服务器
    :param server_path: 服务器路径
    :param server_name: 服务器名称
    :param rewrite: 是否覆盖同名服务器
    """
    # 获取绝对路径
    server_path = os.path.abspath(server_path)

    server_core = find_file.find_files_with_extension(server_path, '.jar')
    log.Debug(server_path)
    log.Debug('找到服务器核心文件：' + str(server_core))
    log.Debug('总共' + str(len(server_core)) + '个文件')
    if len(server_core) == 0:
        log.logger.error('未找到服务器核心文件，请检查文件路径是否正确！')
        return
    else:
        #若找到多个核心文件，排除server.jar文件,填入其他核心
        if len(server_core) > 1:
            for i in range(len(server_core)):
                exclude_keywords = {
                    'server.jar',
                    'com',
                    'commons-io',
                    'cpw',
                    'de',
                    'io',
                    'it',
                    'org',
                    'trove',
                    'java',
                    'jodah',
                    'mincraftforge',
                    'minecrell',
                    'sf'
                }

    # 筛选不包含任意关键词的元素
                server_core = [
                    item for item in server_core
                    if not any(keyword in item for keyword in exclude_keywords)
                ]
        server_core = server_core[0]
        log.Debug('找到服务器核心文件：' + server_core)
        if find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.server_save_path):
            find_file.find_files_with_existence_and_create(server_path + program_info.server_start_batch)

            server_absolute_path = server_path + program_info.server_start_batch
            os.path.abspath(server_absolute_path)
            log.Debug("找到服务器启动批处理文件,位置:" + server_absolute_path)

            try:
                java_args: str = ''
                v = version.parse(server_version)
                with open('./java_versions.json', 'r', encoding='utf-8') as f:
                    java_versions_address = json.load(f)

                    # 按照版本使用不同版本的Java JDK
                    # 获取Java版本
                    if v < version.parse('1.17.0'):
                        java_args = '"' f'{java_versions_address['1.8']}' '"'
                    elif v > version.parse('1.17.0') and v <= version.parse('1.18.2'):
                        java_args = '"' f'{java_versions_address['16']}' '"'
                    elif v > version.parse('1.18.2') and v <= version.parse('1.20.1'):
                        java_args = '"' f'{java_versions_address['17']}' '"'
                    elif v > version.parse('1.20.1') and v <= version.parse('1.21.5'):
                        java_args = '"' f'{java_versions_address['21']}' '"'

                with open(server_path + program_info.server_start_batch, 'w') as f:
                    f.write('cd ' + server_path + '\n')
                    if find_file.find_files_with_existence(server_path + program_info.server_start_batch):
                        try:
                            with open(server_path + program_info.forge_server_start_batch_default_name, 'r') as fi:
                                log.Debug('发现run.bat文件,开始读取...')
                                server_start_command = None
                                for line in fi:
                                    if 'java' in line:
                                        server_start_command = line.strip()
                                        break
                                if server_start_command is None:
                                    log.logger.warning('未找到包含java的命令')
                                    log.logger.info('使用默认启动核心命令:')

                                    f.write(f'{java_args} -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core)
                                else:
                                    log.Debug('读取服务器启动批处理文件成功!')
                                    log.Debug('服务器启动核心命令:' + server_start_command + '\n')
                                    server_start_command = server_start_command.replace(program_info.forge_server_JVM_args, '-Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M')
                                    f.write(server_start_command)
                        except Exception as e:
                            log.logger.error('服务器启动批处理文件读取失败!')
                            log.logger.error(e)
                            f.write(f'{java_args} -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core)
                    else:
                        f.write(f'{java_args} -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core)
                    if program_info.server_start_nogui == "true":
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
            if find_file.find_files_with_existence_and_create(server_path + program_info.eula):
                with open(server_path + program_info.eula, 'w') as f:
                    f.write('eula=true')

            if find_folder.find_folders_with_existence(server_path):
                server_size = size_change.size_change(get.get_dir_size(server_path))

            if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
                if rewrite == True:
                    log.logger.warning('已存在同名服务器，尝试覆盖原信息！')
                    try:
                        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r') as f:
                            server_info = json.load(f)
                            try:
                                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w') as f:
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
                if find_file.find_files_with_existence_and_create(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
                    start_count = 0
                    # server_version = "0.0.0"
                    server_info = {
                        'server_name': server_name,
                        'start_count': start_count,
                        'server_core': server_core,
                        'server_path': server_path,
                        'server_start_batch_path': server_absolute_path,
                        'server_size': server_size,
                        'server_version': server_version,
                        'LatestStartedTime': 'N/A'
                    }
                    try:
                        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w') as f:
                            json.dump(server_info, f, indent=4)
                            f.close()
                        timer.TimerStorageSizeUpdate.thread()
                    except Exception as e:
                        log.logger.error('创建服务器信息文件失败!')
                        log.logger.error(e)
                        return
                else:
                    log.logger.error('创建服务器信息文件失败!')

        program_info.server_list.append(server_name)

def start_server(server_name):
    """
    启动服务器
    :param server_name: 服务器名称
    """
    if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
        try:
            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r') as f:
                server_info = json.load(f)
                if not 'LatestStartedTime' in server_info:
                    server_info['LatestStartedTime'] = get_time.DetailedTime()
                f.close()
        except Exception as e:
            log.logger.error('读取服务器信息文件失败!')
            log.logger.error(e)
            return False
        #设置服务器rcon端口
        try:
            port = None

            if server_info['start_count'] == 0:
                log.logger.warning('服务器从未启动,无法找到server.properties文件！')
            elif server_info['start_count'] == 1:
                if find_file.find_files_with_existence(server_info['server_path'] + program_info.server_properties):
                    log.logger.info('已找到server.properties文件！')
                    log.logger.info('正在设置rcon端口...')
                    port = rcon.set_rcon(server_info)
        except Exception as e:
            log.logger.error('设置rcon端口失败!')
            log.logger.error(e)
            return False
        try:
            start.start_file(server_info['server_start_batch_path'])
        except Exception as e:
            log.logger.error('启动服务器失败！')
            log.logger.error(e)
            return False
        log.logger.info('启动服务器成功！')
        log.logger.info('当前启动服务器:' + server_name)
        time.sleep(2)
        if server_info['start_count'] == 0:
            log.logger.info("服务器第一次启动，请等待服务器启动完成！")
            # time.sleep(program_info.wait_server_eula_generate_time)
            if find_file.find_files_with_existence(server_info['server_path'] + program_info.server_eula):
                log.logger.info('eula协议存在')
                server_info = eula.examine_eula(server_info)
            else:
                log.logger.error('eula协议不存在, 服务器未正常启动, 请重新启动服务器！')
                return False
        else:
            if server_info['start_count'] >= 1:
                server_info = eula.examine_eula(server_info)

        time.sleep(program_info.wait_server_eula_generate_time)

        try:
            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w') as f:
                json.dump(server_info, f, indent=4)
                f.close()
        except Exception as e:
            log.logger.error('修改服务器信息文件失败!')
            log.logger.error(e)
            return False

        # 获取端口
        with open(server_info['server_path'] + program_info.server_properties, 'r', encoding='utf-8') as f:
            log.logger.info('正在获取服务器端口...')
            lines = f.readlines()
            matched_lines = []
            for line_number, line in enumerate(lines, start=1):
                if 'server-port' in line:
                    matched_lines.append((line_number, line))
                    server_port = int(lines[line_number - 1].split('=')[1].strip())
        # 输出latest文件
        try:
            StartTime = get_time.DetailedTime()
            if find_file.find_files_with_existence_and_create(program_info.work_path + program_info.latest_start_server):
                with open(program_info.work_path + program_info.latest_start_server, 'w', encoding='utf-8') as f:
                    f.write('服务器名称:' + server_name + '\n')
                    f.write(str(server_info) + '\n')
                    f.write('服务器端口:' + str(server_port) + '\n')
                    f.write('RCON端口:' + (str(port) if port else "未启用") + '\n')
                    f.write('启动时间:' + StartTime)
                    f.close()
                    log.logger.info('已输出latest.txt文件！')
            if find_file.find_files_with_existence_and_create(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json):
                with open(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json, 'w', encoding='utf-8') as f:
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

def server_list(ShowMessage = True):
    """
    列出服务器列表
    """
    server_list = find_file.find_files_with_extension(program_info.work_path + program_info.server_save_path, '.json')
    if len(server_list) == 0:
        log.logger.error('未找到服务器，请添加服务器！')
        return
    else:
        server_lists = []
        if ShowMessage:
            log.logger.info('当前服务器列表：')
        for server in server_list:
            try:
                with open(server, 'r', encoding='utf-8') as f:
                    server_info = json.load(f)
                    now_server_name = server_info['server_name']
                    f.close()
                if ShowMessage:
                    log.logger.info(now_server_name)
                server_lists.append(now_server_name)
            except Exception as e:
                log.logger.error('读取服务器信息文件失败!')
                log.logger.error(e)
                return
        if ShowMessage:
            log.logger.info('当前服务器数量：' + str(len(server_list)))
        return server_lists

def change_server_properties(server_name, keyword, argument):
    """
    修改服务器属性
    :param server_name: 服务器名称
    :param keyword: 关键字
    :param argument: 参数
    """
    try:
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
            server_info = json.load(f)
            f.close()
        find_file.find_keyword_inline_and_change_argument(server_info['server_path'] + program_info.server_properties, keyword, argument)
    except Exception as e:
        log.logger.error('修改服务器属性失败！')
        log.logger.error(e)

def open_server_mod_and_plugins_folder(server_name):
    """
    打开服务器模组&插件文件夹
    :param server_name: 服务器名称
    """
    try:
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
            server_info = json.load(f)
            f.close()
    except Exception as e:
        log.logger.error('打开服务器模组&插件文件夹失败！')
        log.logger.error(e)
        return

    if find_folder.find_folders_with_existence(server_info['server_path'] + program_info.server_mods_folder) or find_folder.find_folders_with_existence(server_info['server_path'] + program_info.server_plugins_folder):
        try:
            start.start_file(server_info['server_path'] + program_info.server_mods_folder)
        except Exception as e:
            log.logger.error('打开服务器模组文件夹失败！')
            log.logger.error(e)
        try:
            start.start_file(server_info['server_path'] + program_info.server_plugins_folder)
        except Exception as e:
            log.logger.error('打开服务器插件文件夹失败！')
            log.logger.error(e)
    else:
        log.logger.error('服务器模组或插件文件夹不存在，请检查服务器是否启动过一次以上！')

def server_start_batch_rewrite_run_memories(server_name, memory_min, memory_max):
    """
    修改服务器启动内存
    :param server_name: 服务器名称
    :param memory_min: 最小内存
    :param memory_max: 最大内存
    """
    server_info = examin.ServerInfoKeys(server_name)
    if server_info == False:
        log.logger.error('未找到服务器，请检查服务器名称是否正确！')
    else:
        try:
            with open(server_info['server_start_batch_path'], 'w', encoding='utf-8') as f:
                log.logger.info('正在修改服务器启动批处理文件...')
                log.logger.info('修改服务器启动内存为：' + str(memory_min) + ' ' + str(memory_max))
                f.write('cd ' + server_info['server_path'] + '\n')
                f.write('java -Xmx' + str(memory_min) + 'M -Xms' + str(memory_max) + 'M -jar ' + server_info['server_core'])
                if program_info.server_start_nogui == "true":
                    f.write(' -nogui')
                else:
                    f.write('')
                f.close()
                log.logger.info('修改完毕！')
        except Exception as e:
            log.logger.error('读取服务器启动批处理文件失败！')
            log.logger.error(e)
            return

def download_server_core(server_name, core_type, core_support_version):
    """
    下载服务器核心
    :param server_name: 服务器名称
    :param core_type: 核心类型
    :param core_support_version: 核心支持版本
    """
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if find_folder.find_folders_with_existence(server_info['server_path']):
            while(1):
                all_files = find_file.find_files_with_extension(server_info['server_path'], '')
                if len(all_files) != 0:
                    log.logger.error('文件夹已有文件')
                    log.logger.info('为服务器文件夹添加 -repeat 字样')
                    server_info['server_name'] += '-repeat'
                    server_info['server_path'] = server_info['server_path'].rstrip('\\') + '-repeat'
                    log.logger.debug(server_info)
                    if find_folder.find_folders_with_existence_and_create(server_info['server_path']):
                        log.logger.info('创建文件夹:' + server_info['server_path'])
                    else:
                        log.logger.error('创建文件夹失败！')
                        return
                else:
                    break
        if server_core.download_server_core(server_info['server_name'], core_type, core_support_version):
            log.logger.info('下载服务器核心成功！')
            log.logger.info('正在修改服务器信息文件...')
            add_server(server_info['server_path'], server_info['server_name'], True, core_support_version)
            return
        else:
            log.logger.error('下载服务器核心失败！')
    except Exception as e:
        log.logger.error('读取服务器信息文件失败！')
        log.logger.error(e)
        log.logger.warning('检测到服务器并未创建,创建服务器...')
        save_core_path = program_info.work_path + program_info.program_server_folder + '/' + server_name
        find_folder.find_folders_with_existence_and_create(save_core_path)
        if server_core.download_server_core(server_name, core_type, core_support_version):
            log.logger.info('创建服务器成功！')
            log.logger.info('正在添加服务器...')
            add_server(save_core_path, server_name, True, core_support_version)
            program_info.server_list = server_list()
            timer.TimerStorageSizeUpdate.thread()
        else:
            log.logger.error('创建服务器失败！')
            return
        return

def delete_server(server_name, double_check):
    """
    删除服务器
    :param server_name: 服务器名称
    :param double_check: 是否二次确认
    """
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
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
            if find_folder.find_folders_with_existence(server_info['server_path']):
                # 删除服务器文件夹
                shutil.rmtree(server_info['server_path'])

                log.logger.info('删除服务器成功！')
                log.logger.info('正在删除服务器信息文件...')
                os.remove(program_info.work_path + program_info.server_save_path + '/' + server_name +'.json')
            log.logger.info('删除完成!')
            return
    except Exception as e:
        log.logger.error('读取服务器信息文件失败！')
        log.logger.error(e)
        return

def search_server(server_name, Output=False):
    """
    搜索服务器
    :param server_name: 服务器名称
    """
    try:
        log.logger.info('正在搜索服务器...')
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            if not 'server_version' in server_info:
                server_info['server_version'] = 'N/A'
            log.Debug('已找到服务器:' + server_info['server_path'])
            log.Debug('已读取服务器信息文件...')
            # 当输出为False时，输出服务器信息
            # 输出服务器信息
            if not Output:
                log.logger.info('服务器信息:')
                log.logger.info('服务器名称: ' + server_info['server_name'])
                log.logger.info('服务器启动次数: ' + str(server_info['start_count']))
                log.logger.info('服务器核心: ' + server_info['server_core'])
                log.logger.info('服务器路径: ' + server_info['server_path'])
                log.logger.info('服务器启动批处理路径: ' + server_info['server_start_batch_path'])
                log.logger.info('服务器大小: ' + str(server_info['server_size']))
                log.logger.info('服务器核心版本: ' + str(server_info['server_version']))
            return server_info
    except Exception as e:
        log.logger.error('读取服务器信息文件失败！')
        log.logger.error(e)
        return

def banned_player(server_name, player_name):
    """
    封禁玩家
    :param server_name: 服务器名称
    :param player_name: 玩家名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def banned_ip(server_name, player_ip):
    """
    封禁玩家
    :param server_name: 服务器名称
    :param player_ip: IP地址
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def op(server_name, player_name):
    """
    添加OP
    :param server_name: 服务器名称
    :param player_name: 玩家名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def unban_player(server_name, player_name):
    """
    解封玩家
    :param server_name: 服务器名称
    :param player_name: 玩家名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def unban_ip(server_name, player_ip):
    """
    解封玩家
    :param server_name: 服务器名称
    :param player_ip: IP地址
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def deop(server_name, player_name):
    """
    取消玩家操作权限
    :param server_name: 服务器名称
    :param player_name: 玩家名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def stop_server(server_name):
    """
    停止服务器
    :param server_name: 服务器名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            port = rcon.rcon_port(server_info)
            if port != None:
                try:
                    server_command = rcon.connect_rcon(port)
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

def rename_server(server_name, new_name):
    """
    重命名服务器
    :param server_name: 服务器名称
    :param new_name: 新服务器名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            log.logger.info('重命名服务器...')
            try:
                server_info['server_name'] = new_name
                log.logger.info('重命名成功！')
                log.logger.info('修改服务器信息文件...')
                try:
                    with open(program_info.work_path + program_info.server_save_path + '/' + new_name + '.json','w', encoding='utf-8') as f:
                        json.dump(server_info, f, indent=4)
                        f.close()
                        os.remove(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json')
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

def redirected_server_path(server_name, new_path):
    """
    重定向服务器路径
    :param server_name: 服务器名称
    """
    log.logger.info('查找服务器...')
    try:
        server_info = examin.ServerInfoKeys(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
            log.logger.info('重定向服务器路径...')
            try:
                log.logger.info('尝试重定向启动脚本和启动批处理文件...')
                try:
                    server_info['server_core'] = server_info['server_core'].replace(server_info['server_path'], new_path)
                    log.logger.info('重定向服务器核心成功！')
                    server_info['server_start_batch_path'] = server_info['server_start_batch_path'].replace(server_info['server_path'], new_path)
                    log.logger.info('重定向服务器启动批处理文件成功！')
                    server_info['server_path'] =   new_path
                    with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
                        json.dump(server_info, f, indent=4)
                    with open(server_info['server_start_batch_path'], 'w') as f:
                        f.write('cd ' + server_info['server_path'] + '\n')
                        f.write('java -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_info['server_core'])
                        if program_info.server_start_nogui == 'true':
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
                    with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json','w', encoding='utf-8') as f:
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

def start_latest_server():
    """
    启动上次启动的服务器
    """
    try:
        server_lists = find_file.find_files_with_existence(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json)
        if server_lists == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return False
        else:
            with open(program_info.work_path + program_info.program_resource + program_info.latest_start_server_json, 'r', encoding='utf-8') as f:
                server_info = json.load(f)
                f.close()
            log.logger.info('已找到服务器:' + server_info['server_name'])
            log.logger.info('启动服务器...')
            inspection_server_started = start_server(server_info['server_name'])
            if inspection_server_started == False:
                log.logger.error('启动服务器失败！')
            else:
                log.logger.info('启动服务器成功！')
                return server_info
    except Exception as e:
        log.logger.error('读取服务器信息文件失败！')
        log.logger.error(e)
        return False

def Restart_Server(server_name):
    """
    重启服务器
    :param server_name: 服务器名称
    """
    try:
        log.logger.info('尝试重启服务器...')
        stop_server(server_name)
        time.sleep(3)
        start_server(server_name)
        log.logger.info('重启服务器成功！')
        return
    except Exception as e:
        log.logger.error('重启服务器失败！')
        log.logger.error(e)
        return

def find_backup_file(server_name):
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
        if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                server_info = json.load(f)
                # mod
                if find_folder.find_folders_with_existence(server_info['server_path'] + '/mods'):
                    mod_list = os.listdir(server_info['server_path'] + '/mods')
                    for mods in mod_list:
                        if 'ftbbackups2' in mods:
                            log.logger.info('已找到FTB Backups 2 模组！')
                            log.logger.info('尝试获取备份列表...')
                            try:
                                log.logger.info('尝试获取FTB Backups 2 备份文件...')
                                backup_list = os.listdir(server_info['server_path'] + '/backups')
                                # 按照时间排序
                                backup_list = sorted(backup_list, key=lambda x: os.path.getmtime(server_info['server_path'] + '/backups/' + x))
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
                if find_folder.find_folders_with_existence(server_info['server_path'] + '/plugins'):
                    plugin_list = os.listdir(server_info['server_path'] + '/plugins')
                    for plusins in plugin_list:
                        if 'ebackup' in plusins:
                            log.logger.info('已找到 eBackup 插件!')
                            log.logger.info('尝试获取备份列表...')
                            try:
                                log.logger.info('尝试获取 eBackup 备份文件...')
                                backup_list = os.listdir(server_info['server_path'] + '/plugins/eBackup/backups')
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

        else:
            log.logger.error('未找到服务器信息文件！')
            return
    except Exception as e:
        log.logger.error('获取服务器信息失败！')
        log.logger.error(e)
        return

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

import stat

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def Retracement(server_name: str, backup_file_name = None):
    """
    回档服务器
    :param server_name: 服务器名称
    """

    if backup_file_name is None:
        log.logger.info('未指定回档文件名，将默认使用最新文件进行回档！')
        try:
            backups = find_backup_file(server_name)
            log.logger.info(f'尝试回档文件：{backups[-2]}')
            backup_file_name = backups[-2]

            # mod
            if backups[-1] == 'mod':
                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                    backup_file_content = json.load(f)
                    backup_file_absolute_path = backup_file_content['server_path'] + '/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files = get_top_level_dirs(backup_file_absolute_path)
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['server_path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['server_path'] + '/' + file, arcname=backup_file_content['server_path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['server_path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['server_path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['server_path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}！')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['server_path'])
                        log.logger.info('解压完成！')

            # plugin
            if backups[-1] == 'plugin':
                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                    backup_file_content = json.load(f)
                    backup_file_absolute_path = backup_file_content['server_path'] + '/plugins/eBackup/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r')as zip_ref:
                        all_files = zip_ref.namelist()
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['server_path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['server_path'] + '/' + file, arcname=backup_file_content['server_path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['server_path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['server_path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['server_path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')
                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['server_path'])
                        log.logger.info('解压完成！')
        except Exception as e:
            log.logger.error(f'解压文件失败!\n{e}')
            return False
    else:
        try:
            backups = find_backup_file(server_name)

            # mod
            if backups[-1] == 'mod':
                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                    backup_file_content = json.load(f)
                    backup_file_absolute_path = backup_file_content['server_path'] + '/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files = get_top_level_dirs(backup_file_absolute_path)
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['server_path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['server_path'] + '/' + file, arcname=backup_file_content['server_path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['server_path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['server_path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['server_path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['server_path'])
                        log.logger.info('解压完成！')

            # plugin
            if backups[-1] == 'plugin':
                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                    backup_file_content = json.load(f)
                    backup_file_absolute_path = backup_file_content['server_path'] + '/plugins/eBackup/backups/' + backup_file_name

                    # 删除旧文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        all_files  = zip_ref.namelist()
                    for file in all_files:
                        with zipfile.ZipFile(backup_file_content['server_path'] + '/' + 'old-save.zip', 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                            zip_ref.write(backup_file_content['server_path'] + '/' + file, arcname=backup_file_content['server_path'] + '/' + file)
                        if find_folder.find_folders_with_existence(backup_file_content['server_path'] + '/' + file):
                            log.logger.debug(f'删除文件路径{backup_file_content['server_path'] + '/' + file}')
                            shutil.rmtree(backup_file_content['server_path'] + '/' + file, onerror=remove_readonly)
                            log.logger.info(f'删除{file}!')

                    # 解压文件
                    with zipfile.ZipFile(backup_file_absolute_path, 'r') as zip_ref:
                        zip_ref.extractall(backup_file_content['server_path'])
                        log.logger.info('解压完成！')
        except Exception as e:
            log.logger.error(f'解压文件失败!{e}')
            return False