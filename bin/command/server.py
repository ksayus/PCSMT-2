import os
import json
import time
import shutil
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import program_info
from bin.command import start
from bin.export import eula
from bin.export import log
from bin.export import examin_json_argument
from bin.download import server_core
def add_server(server_path, server_name, rewrite):
    server_core = find_file.find_files_with_extension(server_path, '.jar')
    log.logger.info('找到服务器核心文件：' + str(server_core))
    log.logger.info('总共' + str(len(server_core)) + '个文件')
    if len(server_core) == 0:
        log.logger.error('未找到服务器核心文件，请检查文件路径是否正确！')
        return
    else:
        #若找到多个核心文件，排除server.jar文件,填入其他核心
        if len(server_core) > 1:
            for i in range(len(server_core)):
                exclude_keywords = {
                    'server.jar', 'com', 'commons-io', 'cpw', 'de', 'io',
                    'it', 'org', 'trove', 'java', 'jodah', 'mincraftforge',
                    'minecrell', 'sf'
                }
    
    # 筛选不包含任意关键词的元素
                server_core = [
                    item for item in server_core
                    if not any(keyword in item for keyword in exclude_keywords)
                ]
        server_core = server_core[0]
        log.logger.info('找到服务器核心文件：' + server_core)
        if find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.server_save_path):
            find_file.find_files_with_existence_and_create(server_path + program_info.server_start_batch)

            server_absolute_path = server_path + program_info.server_start_batch
            os.path.abspath(server_absolute_path)
            log.logger.info("找到服务器启动批处理文件,位置:" + server_absolute_path)

            try:
                with open(server_path + program_info.server_start_batch, 'w') as f:
                    f.write('cd ' + server_path + '\n')
                    if find_file.find_files_with_existence(server_path + program_info.server_start_batch):
                        try:
                            with open(server_path + program_info.forge_server_start_batch_default_name, 'r') as fi:
                                log.logger.info('发现run.bat文件,开始读取...')
                                server_start_command = None
                                for line in fi:
                                    if 'java' in line:
                                        server_start_command = line.strip()
                                        break
                                if server_start_command is None:
                                    log.logger.warning('未找到包含java的命令,请检查run.bat文件是否正确！')
                                    f.write('java -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core + ' nogui')
                                else:
                                    log.logger.info('读取服务器启动批处理文件成功!')
                                    log.logger.info('服务器启动核心命令:' + server_start_command + '\n')
                                    server_start_command = server_start_command.replace(program_info.forge_server_JVM_args, '-Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M')
                                    f.write(server_start_command)
                        except Exception as e:
                            log.logger.error('服务器启动批处理文件读取失败!')
                            log.logger.error(e)
                            f.write('java -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core + ' nogui')
                    else:
                        f.write('java -Xms' + str(program_info.default_server_run_memories_min) + 'M -Xmx' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core + ' nogui')
                    if program_info.server_start_nogui == "true":
                        f.write(' -nogui')
                    else:
                        f.write('')
                    f.close()
            except Exception as e:
                log.logger.error('创建服务器启动批处理文件失败!')
                log.logger.error(e)
                return
            
            if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
                if rewrite == True:
                    log.logger.warning('已存在同名服务器，尝试覆盖原信息！')
                    try:
                        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r') as f:
                            server_info = json.load(f)
                            server_info_rewrite = {
                                'server_name': server_info['server_name'],
                                'start_count': server_info['start_count'],
                                'server_core': server_core,
                                'server_path': server_path,
                                'server_start_batch_path': server_absolute_path
                            }
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
                    server_info = {
                        'server_name': server_name,
                        'start_count': start_count,
                        'server_core': server_core,
                        'server_path': server_path,
                        'server_start_batch_path': server_absolute_path
                    }
                    try:
                        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w') as f:
                            json.dump(server_info, f, indent=4)
                            f.close()
                    except Exception as e:
                        log.logger.error('创建服务器信息文件失败!')
                        log.logger.error(e)
                        return
                else:
                    log.logger.error('创建服务器信息文件失败!')

def start_server(server_name):
    if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json'):
        try:
            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r') as f:
                server_info = json.load(f)
                f.close()
        except Exception as e:
            log.logger.error('读取服务器信息文件失败!')
            log.logger.error(e)
            return
        try:
            start.start_file(server_info['server_start_batch_path'])
        except Exception as e:
            log.logger.error('启动服务器失败！')
            log.logger.error(e)
            return
        log.logger.info('启动服务器成功！')
        log.logger.info('当前启动服务器:' + server_name)
        if server_info['start_count'] == 0:
            log.logger.info("服务器第一次启动，请等待服务器启动完成！")
            time.sleep(15)
            if find_file.find_files_with_existence(server_info['server_path'] + program_info.server_eula):
                log.logger.info('eula协议存在')
                server_info = eula.examine_eula(server_info)
            else:
                log.logger.error('eula协议不存在, 服务器未正常启动, 请重新启动服务器！')
                return
        else:
            if server_info['start_count'] >= 1:
                server_info = eula.examine_eula(server_info)
        try:
            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w') as f:
                json.dump(server_info, f, indent=4)
                f.close()
        except Exception as e:
            log.logger.error('修改服务器信息文件失败!')
            log.logger.error(e)
            return
    else:
        log.logger.error('未找到服务器，请检查服务器名称是否正确！')
        return
    
def server_list():
    server_list = os.listdir(program_info.work_path + program_info.server_save_path)
    if len(server_list) == 0:
        log.logger.error('未找到服务器，请添加服务器！')
        return
    else:
        log.logger.info('当前服务器列表：')
        for server in server_list:
            if server == '.DS_Store':
                continue
            if server == '__pycache__':
                continue
            if server == '__init__.py':
                continue
            if server == '__init__.pyc':
                continue
            if server == '__init__.pyo':
                continue
            
            with open(program_info.work_path + program_info.server_save_path + '/' + server, 'r', encoding='utf-8') as f:
                server_info = json.load(f)
                now_server_name = server_info['server_name']
                f.close()

            log.logger.info(now_server_name)
        log.logger.info('当前服务器数量：' + str(len(server_list)))

def change_server_properties(server_name, keyword, argument):
    try:
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
            server_info = json.load(f)
            f.close()
        find_file.find_keyword_inline_and_change_argument(server_info['server_path'] + program_info.server_properties, keyword, argument)
    except Exception as e:
        log.logger.error('修改服务器属性失败！')
        log.logger.error(e)

def open_server_mod_and_plugins_folder(server_name):
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
    server_info = examin_json_argument.examin_saves_json_argument(server_name)
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
    try:
        server_info = examin_json_argument.examin_saves_json_argument(server_name)
        find_folder.find_folders_with_existence_and_create(server_info['server_path'])
        if server_core.download_server_core(server_name, core_type, core_support_version):
            log.logger.info('下载服务器核心成功！')
            log.logger.info('正在修改服务器信息文件...')
            add_server(server_info['server_path'], server_name, True)
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
            add_server(save_core_path, server_name, True)
        else:
            log.logger.error('创建服务器失败！')
            return
        return
    
def delete_server(server_name):
    try:
        server_info = examin_json_argument.examin_saves_json_argument(server_name)
        if server_info == False:
            log.logger.error('未找到服务器，请检查服务器名称是否正确！')
            return
        else:
            log.logger.info('已找到服务器:' + server_info['server_path'])
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