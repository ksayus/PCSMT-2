import os
import json
import time
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import program_info
from bin.command import start
from bin.export import eula
from bin.export import log
from bin.export import examin_json_argument
def add_server(server_path, server_name):
    server_core = find_file.find_files_with_extension(server_path, '.jar')
    if len(server_core) == 0:
        log.logger.error('未找到服务器核心文件，请检查文件路径是否正确！')
        return
    else:
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
                    f.write('java -Xmx' + str(program_info.default_server_run_memories_min) + 'M -Xms' + str(program_info.default_server_run_memories_max) + 'M -jar ' + server_core + ' nogui')
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
                log.logger.warning('已存在同名服务器，请更换服务器名称！')
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
            time.sleep(5)
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