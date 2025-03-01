from bin.find_files import find_folder, find_file
from bin.introduction import introduction
from bin.export import program_info
from bin.export import get_time
from bin.export import log
from bin.download import update
from bin.command import program
import json
import sys

def init_program():
    """
    初始化程序
    """
    try:
        program.Delete_old_program()
        if program_info.Auto_Update_Source == "Github":
            result = update.update_program_github()
            if result == 0:
                log.logger.info("GitHub 更新失败,尝试 Gitee 更新...")
                result = update.update_program_gitee()
                if result == 0:
                    log.logger.info("无法完成自动更新,请手动更新!")
        elif program_info.Auto_Update_Source == "Gitee":
            result = update.update_program_gitee()
            if result == 0:
                log.logger.info("Gitee 更新失败,尝试 Github 更新...")
                result = update.update_program_github()
                if result == 0:
                    log.logger.info("无法完成自动更新,请手动更新!")
        if program_info.Automatic_startup == True:
            program.add_to_startup(program_info.program_name)
        elif program_info.Automatic_startup == False:
            program.remove_from_startup(program_info.program_name)
        find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.server_save_path)
        find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.program_logs)
        find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.program_server_folder)

        introduction.Homepage()
    except Exception as e:
        log.logger.error('初始化程序失败！')
        log.logger.error(e)
        sys.exit()

def read_config_json():
    """
    读取config.json文件
    检查config.json文件是否存在,不存在则创建,存在则读取
    读取后检查config.json文件中的信息,如果信息不匹配则更新config.json文件
    :return: config_read
    """
    if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
        log.logger.info('已存在config文件')
        try:
            with open(program_info.work_path + program_info.program_config, 'r') as f:
                config_read = json.load(f)
                if not config_read:
                    log.logger.warning('config文件已存在，但配置为空')
                    log.logger.info('写入配置')
                    config_read = program_info.config
                    return config_read
                else:
                    #Version
                    if not 'PCSMTVersion' in config_read:
                        log.logger.warning('config文件已存在，但不存在版本号关键字')
                        log.logger.info('写入版本号')
                        config_read['PCSMTVersion'] = program_info.config['PCSMTVersion']
                    else:
                        if config_read['PCSMTVersion'] == None:
                            log.logger.warning('config文件已存在，但版本号未设置')
                            log.logger.info('写入版本号')
                            config_read['PCSMTVersion'] = program_info.config['PCSMTVersion']
                        else:
                            if config_read['PCSMTVersion'] != program_info.config['PCSMTVersion']:
                                log.logger.warning('config文件已存在，但版本号不匹配')
                                log.logger.info('写入版本号')
                                config_read['PCSMTVersion'] = program_info.config['PCSMTVersion']

                    #Release_Version
                    if not 'Release_Version' in config_read:
                        log.logger.warning('config文件已存在，但不存在版本号关键字')
                        log.logger.info('写入版本号')
                        config_read['Release_Version'] = program_info.config['Release_Version']
                    else:
                        if config_read['Release_Version'] == None:
                            log.logger.warning('config文件已存在，但版本号未设置')
                            log.logger.info('写入版本号')
                            config_read['Release_Version'] = program_info.config['Release_Version']
                        else:
                            if config_read['Release_Version'] != program_info.config['Release_Version']:
                                log.logger.warning('config文件已存在，但版本号不匹配')
                                log.logger.info('写入版本号')
                                config_read['Release_Version'] = program_info.config['Release_Version']

                    #default_server_run_memories_min
                    if not 'default_server_run_memories_min' in config_read:
                        log.logger.warning('config文件已存在，但最小内存关键字不存在')
                        log.logger.info('写入最小内存')
                        config_read['default_server_run_memories_min'] = program_info.config['default_server_run_memories_min']
                    else:
                        if config_read['default_server_run_memories_min'] == None:
                            log.logger.warning('config文件已存在，但最小内存未设置')
                            log.logger.info('写入最小内存')
                            config_read['default_server_run_memories_min'] = program_info.config['default_server_run_memories_min']

                    #default_server_run_memories_max
                    if not 'default_server_run_memories_max' in config_read:
                        log.logger.warning('config文件已存在，但最大内存关键字不存在')
                        log.logger.info('写入最大内存')
                        config_read['default_server_run_memories_max'] = program_info.config['default_server_run_memories_max']
                    else:
                        if config_read['default_server_run_memories_max'] == None:
                            log.logger.warning('config文件已存在，但最大内存未设置')
                            log.logger.info('写入最大内存')
                            config_read['default_server_run_memories_max'] = program_info.config['default_server_run_memories_max']

                    #server_start_nogui
                    if not 'server_start_nogui' in config_read:
                        log.logger.warning('config文件已存在，但启用图形界面关键字不存在')
                        log.logger.info('写入启用图形界面参数为True')
                        config_read['server_start_nogui'] = program_info.config['server_start_nogui']
                    else:
                        if config_read['server_start_nogui'] == None:
                            log.logger.warning('config文件已存在，但启用图形界面未设置')
                            log.logger.info('写入启用图形界面参数为True')
                            config_read['server_start_nogui'] = program_info.config['server_start_nogui']

                    #wait_server_eula_generate_time
                    if not 'wait_server_eula_generate_time' in config_read:
                        log.logger.warning('config文件已存在，但等待eula生成时间关键字不存在')
                        log.logger.info('写入等待eula生成时间参数为默认值')
                        config_read['wait_server_eula_generate_time'] = program_info.config['wait_server_eula_generate_time']
                    else:
                        if config_read['wait_server_eula_generate_time'] == None:
                            log.logger.warning('config文件已存在，但等待eula生成时间未设置')
                            log.logger.info('写入等待eula生成时间参数为默认值')
                            config_read['wait_server_eula_generate_time'] = program_info.config['wait_server_eula_generate_time']

                    #Automatic_startup
                    if not 'Automatic_startup' in config_read:
                        log.logger.warning('config文件已存在，但自动启动关键字不存在')
                        log.logger.info('写入自动启动参数为True')
                        config_read['Automatic_startup'] = program_info.config['Automatic_startup']
                    else:
                        if config_read['Automatic_startup'] == None:
                            log.logger.warning('config文件已存在，但自动启动未设置')
                            log.logger.info('写入自动启动参数为True')
                            config_read['Automatic_startup'] = program_info.config['Automatic_startup']

                    #Auto_Update_Source
                    if not 'Auto_Update_Source' in config_read:
                        log.logger.warning('config文件已存在，但自动更新源关键字不存在')
                        log.logger.info('写入自动更新源参数为Github')
                        config_read['Auto_Update_Source'] = program_info.config['Auto_Update_Source']
                    else:
                        if config_read['Auto_Update_Source'] == None:
                            log.logger.warning('config文件已存在，但自动更新源未设置')
                            log.logger.info('写入自动更新源参数为Github')
                            config_read['Auto_Update_Source'] = program_info.config['Auto_Update_Source']
                        else:
                            if config_read['Auto_Update_Source'] != 'Github' and config_read['Auto_Update_Source'] != 'Gitee':
                                log.logger.warning('config文件已存在，但自动更新源设置错误')
                                log.logger.info('写入自动更新源参数为Github')
                                config_read['Auto_Update_Source'] = program_info.config['Auto_Update_Source']



                    try:
                        with open(program_info.work_path + program_info.program_config, "w") as f:
                            f.write(json.dumps(config_read, indent=4))
                            return config_read
                            f.close()
                    except Exception as e:
                        log.logger.error('写入config文件失败')
                        log.logger.error(e)
                        f.close()

        except Exception as e:
            log.logger.error('读取config文件失败')
            log.logger.error(e)


    else:
        if find_file.find_files_with_existence_and_create(program_info.work_path + program_info.program_config):
                with open(program_info.work_path + program_info.program_config, "w") as f:
                    config_read = program_info.config
                    f.write(json.dumps(config_read, indent=4))
                    return config_read
                    f.close()
        else:
            log.logger.error("创建config文件失败!")