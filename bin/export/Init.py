from bin.find_files import find_folder, find_file
from bin.introduction import introduction
from bin.export import Info
from bin.export import log
from bin.download import Update
from bin.command import Program
import json
import sys
import os

class Infomation:
    def Program():
        """
        初始化程序
        """
        try:
            Info.work_path = os.getcwd()  # 显式设置工作路径为字符串类型

            Program.Processing.Delete_Script()
            if Info.Config.AutoUpdateSource() == "Github":
                result = Update.Source.Github()
                if result == 0:
                    log.logger.info("GitHub 更新失败,尝试 Gitee 更新...")
                    result = Update.Source.Gitee()
                    if result == 0:
                        log.logger.info("无法完成自动更新,请手动更新!")
            elif Info.Config.AutoUpdateSource() == "Gitee":
                result = Update.Source.Gitee()
                if result == 0:
                    log.logger.info("Gitee 更新失败,尝试 Github 更新...")
                    result = Update.Source.Github()
                    if result == 0:
                        log.logger.info("无法完成自动更新,请手动更新!")
            if Info.Config.AutomaticStartup() == True:
                Program.Do.AddStartup(Info.program_name)
            elif Info.Config.AutomaticStartup() == False:
                Program.Do.RemoveStartup(Info.program_name)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Resource)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Resource + Info.File.Folder.CoreInstallation)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Resource + Info.File.Folder.Excel)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Save)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Logs)
            find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.Servers)


            introduction.Homepage()
        except Exception as e:
            log.logger.error('初始化程序失败！')
            log.logger.error(e)
            sys.exit()

    def Config():
        """
        读取config.json文件
        检查config.json文件是否存在,不存在则创建,存在则读取
        读取后检查config.json文件中的信息,如果信息不匹配则更新config.json文件
        :return: config_read
        """
        if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
            log.logger.info('已存在config文件')
            try:
                with open(Info.work_path + Info.File.Document.Config, 'r', encoding='utf-8') as f:
                    # 单独捕获JSON解析异常
                    try:
                        config_read = json.load(f)
                    except json.JSONDecodeError as e:
                        log.logger.error('config文件格式错误，将使用默认配置覆盖')
                        log.logger.error(e)
                        # 初始化默认配置并写入
                        config_read = Info.Config.Config.copy()
                        with open(Info.work_path + Info.File.Document.Config, "w", encoding='utf-8') as f_write:
                            f_write.write(json.dumps(config_read, indent=4))
                            f_write.flush()
                            os.fsync(f_write.fileno())
                        return config_read

                    # 添加空配置检查
                    if not config_read:
                        log.logger.warning('config文件内容为空，初始化默认配置')
                        config_read = Info.Config.Config.copy()  # 使用copy避免引用问题
                        # 立即写入修复后的配置
                        with open(Info.work_path + Info.File.Document.Config, "w", encoding='utf-8') as f_write:
                            f_write.write(json.dumps(config_read, indent=4))
                            f_write.flush()
                            os.fsync(f_write.fileno())
                        return config_read

                    #PCSMT2_Version
                    if not 'PCSMT2_Version' in config_read:
                        log.logger.warning('config文件已存在，但不存在版本号关键字')
                        log.logger.info('写入版本号')
                        config_read['PCSMT2_Version'] = Info.Config.Config['PCSMT2_Version']
                    else:
                        if config_read['PCSMT2_Version'] == None:
                            log.logger.warning('config文件已存在，但版本号未设置')
                            log.logger.info('写入版本号')
                            config_read['PCSMT2_Version'] = Info.Config.Config['PCSMT2_Version']
                        else:
                            if config_read['PCSMT2_Version'] != Info.Config.Config['PCSMT2_Version']:
                                log.logger.warning('config文件已存在，但版本号不匹配')
                                log.logger.info('写入版本号')
                                config_read['PCSMT2_Version'] = Info.Config.Config['PCSMT2_Version']

                    #ReleaseVersion
                    if not 'ReleaseVersion' in config_read:
                        log.logger.warning('config文件已存在，但不存在版本号关键字')
                        log.logger.info('写入版本号')
                        config_read['ReleaseVersion'] = Info.Config.Config['ReleaseVersion']
                    else:
                        if config_read['ReleaseVersion'] == None:
                            log.logger.warning('config文件已存在，但版本号未设置')
                            log.logger.info('写入版本号')
                            config_read['ReleaseVersion'] = Info.Config.Config['ReleaseVersion']
                        else:
                            if config_read['ReleaseVersion'] != Info.Config.Config['ReleaseVersion']:
                                log.logger.warning('config文件已存在，但版本号不匹配')
                                log.logger.info('写入版本号')
                                config_read['ReleaseVersion'] = Info.Config.Config['ReleaseVersion']

                    #RunningMemories_Min
                    if not 'RunningMemories_Min' in config_read:
                        log.logger.warning('config文件已存在，但最小内存关键字不存在')
                        log.logger.info('写入最小内存')
                        config_read['RunningMemories_Min'] = Info.Config.Config['RunningMemories_Min']
                    else:
                        if config_read['RunningMemories_Min'] == None:
                            log.logger.warning('config文件已存在，但最小内存未设置')
                            log.logger.info('写入最小内存')
                            config_read['RunningMemories_Min'] = Info.Config.Config['RunningMemories_Min']

                    #RunningMemories_Max
                    if not 'RunningMemories_Max' in config_read:
                        log.logger.warning('config文件已存在，但最大内存关键字不存在')
                        log.logger.info('写入最大内存')
                        config_read['RunningMemories_Max'] = Info.Config.Config['RunningMemories_Max']
                    else:
                        if config_read['RunningMemories_Max'] == None:
                            log.logger.warning('config文件已存在，但最大内存未设置')
                            log.logger.info('写入最大内存')
                            config_read['RunningMemories_Max'] = Info.Config.Config['RunningMemories_Max']

                    #Nogui
                    if not 'Nogui' in config_read:
                        log.logger.warning('config文件已存在，但启用图形界面关键字不存在')
                        log.logger.info('写入启用图形界面参数为True')
                        config_read['Nogui'] = Info.Config.Config['Nogui']
                    else:
                        if config_read['Nogui'] == None:
                            log.logger.warning('config文件已存在，但启用图形界面未设置')
                            log.logger.info('写入启用图形界面参数为True')
                            config_read['Nogui'] = Info.Config.Config['Nogui']

                    #WaitEulaGenerateTime
                    if not 'WaitEulaGenerateTime' in config_read:
                        log.logger.warning('config文件已存在，但等待eula生成时间关键字不存在')
                        log.logger.info('写入等待eula生成时间参数为默认值')
                        config_read['WaitEulaGenerateTime'] = Info.Config.Config['WaitEulaGenerateTime']
                    else:
                        if config_read['WaitEulaGenerateTime'] == None:
                            log.logger.warning('config文件已存在，但等待eula生成时间未设置')
                            log.logger.info('写入等待eula生成时间参数为默认值')
                            config_read['WaitEulaGenerateTime'] = Info.Config.Config['WaitEulaGenerateTime']

                    #AutomaticStartup
                    if not 'AutomaticStartup' in config_read:
                        log.logger.warning('config文件已存在，但自动启动关键字不存在')
                        log.logger.info('写入自动启动参数为True')
                        config_read['AutomaticStartup'] = Info.Config.Config['AutomaticStartup']
                    else:
                        if config_read['AutomaticStartup'] == None:
                            log.logger.warning('config文件已存在，但自动启动未设置')
                            log.logger.info('写入自动启动参数为True')
                            config_read['AutomaticStartup'] = Info.Config.Config['AutomaticStartup']

                    #AutoUpdateSource
                    if not 'AutoUpdateSource' in config_read:
                        log.logger.warning('config文件已存在，但自动更新源关键字不存在')
                        log.logger.info('写入自动更新源参数为Github')
                        config_read['AutoUpdateSource'] = Info.Config.Config['AutoUpdateSource']
                    else:
                        if config_read['AutoUpdateSource'] == None:
                            log.logger.warning('config文件已存在，但自动更新源未设置')
                            log.logger.info('写入自动更新源参数为Github')
                            config_read['AutoUpdateSource'] = Info.Config.Config['AutoUpdateSource']
                        else:
                            if config_read['AutoUpdateSource'] != 'Github' and config_read['AutoUpdateSource'] != 'Gitee':
                                log.logger.warning('config文件已存在，但自动更新源设置错误')
                                log.logger.info('写入自动更新源参数为Github')
                                config_read['AutoUpdateSource'] = Info.Config.Config['AutoUpdateSource']

                    #MinecraftTestVersion
                    if not 'MinecraftTestVersion' in config_read:
                        log.logger.warning('config文件已存在，但测试版本关键字不存在')
                        log.logger.info('写入测试版本参数为False')
                        config_read['MinecraftTestVersion'] = Info.Config.Config['MinecraftTestVersion']
                    else:
                        if config_read['MinecraftTestVersion']== None:
                            log.logger.warning('config文件已存在，但测试版本未设置')
                            log.logger.info('写入测试版本参数为False')
                            config_read['MinecraftTestVersion'] = Info.Config.Config['MinecraftTestVersion']

                    #StorageSizeUpdateTime
                    if not 'StorageSizeUpdateTime' in config_read:
                        log.logger.warning('config文件已存在，但存储空间更新时间关键字不存在')
                        log.logger.info('写入存储空间更新时间参数为默认值')
                        config_read['StorageSizeUpdateTime'] = Info.Config.Config['StorageSizeUpdateTime']
                    else:
                        if config_read['StorageSizeUpdateTime'] == None:
                            log.logger.warning('config文件已存在，但存储空间更新时间未设置')
                            log.logger.info('写入存储空间更新时间参数为默认值')
                            config_read['StorageSizeUpdateTime'] = Info.Config.Config['StorageSizeUpdateTime']


                    try:
                        with open(Info.work_path + Info.File.Document.Config, "w") as f:
                            f.write(json.dumps(config_read, indent=4))
                            return config_read
                    except Exception as e:
                        log.logger.error('写入config文件失败')
                        log.logger.error(e)
                        return Info.Config.Config.copy()  # 返回默认配置保证程序继续运行

            except Exception as e:
                log.logger.error('读取config文件失败')
                log.logger.error(e)
                return Info.Config.Config.copy()  # 返回默认配置保证程序继续运行

        else:
            if find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Document.Config):
                try:
                    with open(Info.work_path + Info.File.Document.Config, "w", encoding='utf-8') as f:
                        config_read = Info.Config.Config.copy()
                        f.write(json.dumps(config_read, indent=4))
                        f.flush()  # 确保写入完成
                        os.fsync(f.fileno())
                        return config_read
                except Exception as e:
                    log.logger.error(f"创建config文件失败: {str(e)}")
                    return Info.Config.Config.copy()
            else:
                log.logger.error("创建config文件失败!")
                return Info.Config.Config.copy()  # 返回默认配置保证程序继续运行