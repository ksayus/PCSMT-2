<<<<<<< HEAD
from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
import os
import requests

def init_core_installer(core_type, core_support_version):
    """
    初始化核心下载器
    :param core_type: 核心类型
    :param core_support_version: 核心支持版本
    """
    if core_type == 'fabric':
        if find_file.find_files_with_existence(program_info.work_path + program_info.fabric_core_installation):
            log.logger.info('Fabric核心下载器已存在')
            return True
        else:
            try:
                log.logger.warning('Fabric核心下载器不存在')
                log.logger.info('正在下载Fabric核心下载器...')
                os.system('powershell curl -o '+ program_info.work_path + program_info.fabric_core_installation + ' https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar')
                log.logger.info('下载完成')
                return True
            except Exception as e:
                log.logger.error('获取Fabric核心下载器失败,请检查')
                return False
    if core_type == 'forge':
        try:
            log.logger.info('尝试下载Forge核心下载器...')
            try:
                response = requests.get('https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json')
                response.json()
                forge_core_version = response.json()['promos'][core_support_version + '-latest']
                log.logger.info('找到到Forge核心: ' + core_support_version + '-' + forge_core_version)
            except Exception as e:
                log.logger.error('获取Forge核心下载器失败,请检查')
                log.logger.error(e)
                return False
            log.logger.info('正在下载Forge核心...')
            try:
                os.system('powershell curl -o '+ program_info.work_path + program_info.forge_core_installation + ' https://maven.minecraftforge.net/net/minecraftforge/forge/'+ core_support_version + '-' + forge_core_version + '/forge-' + core_support_version + '-' + forge_core_version + '-installer.jar')
                log.logger.info('下载完成')
                return True
            except Exception as e:
                log.logger.error('下载Forge核心失败,请检查')
                log.logger.error(e)
                return False
        except Exception as e:
            log.logger.error('下载Forge核心失败,请检查')
            log.logger.error(e)
            return False
    # if core_type == 'spigot':
    #     if find_file.find_files_with_existence(program_info.work_path + program_info.spigot_core_installation):
    #         log.logger.info('Spigot核心下载器已存在')
    #         return True
    #     else:
    #         try:
    #             log.logger.warning('Fabric核心下载器不存在')
    #             log.logger.info('正在下载Fabric核心下载器...')
    #             os.system('powershell curl -o '+ program_info.work_path + program_info.spigot_core_installation + ' https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.exe')
    #             log.logger.info('下载完成')
    #             return True
    #         except Exception as e:
    #             log.logger.error('获取Fabric核心下载器失败,请检查')
=======
from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
import os
import requests

def init_core_installer(core_type, core_support_version):
    """
    初始化核心下载器
    :param core_type: 核心类型
    :param core_support_version: 核心支持版本
    """
    if core_type == 'fabric':
        if find_file.find_files_with_existence(program_info.work_path + program_info.fabric_core_installation):
            log.logger.info('Fabric核心下载器已存在')
            return True
        else:
            try:
                log.logger.warning('Fabric核心下载器不存在')
                log.logger.info('正在下载Fabric核心下载器...')
                os.system('powershell curl -o '+ program_info.work_path + program_info.fabric_core_installation + ' https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar')
                log.logger.info('下载完成')
                return True
            except Exception as e:
                log.logger.error('获取Fabric核心下载器失败,请检查')
                return False
    if core_type == 'forge':
        try:
            log.logger.info('尝试下载Forge核心下载器...')
            try:
                response = requests.get('https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json')
                response.json()
                forge_core_version = response.json()['promos'][core_support_version + '-latest']
                log.logger.info('找到到Forge核心: ' + core_support_version + '-' + forge_core_version)
            except Exception as e:
                log.logger.error('获取Forge核心下载器失败,请检查')
                log.logger.error(e)
                return False
            log.logger.info('正在下载Forge核心...')
            try:
                os.system('powershell curl -o '+ program_info.work_path + program_info.forge_core_installation + ' https://maven.minecraftforge.net/net/minecraftforge/forge/'+ core_support_version + '-' + forge_core_version + '/forge-' + core_support_version + '-' + forge_core_version + '-installer.jar')
                log.logger.info('下载完成')
                return True
            except Exception as e:
                log.logger.error('下载Forge核心失败,请检查')
                log.logger.error(e)
                return False
        except Exception as e:
            log.logger.error('下载Forge核心失败,请检查')
            log.logger.error(e)
            return False
    # if core_type == 'spigot':
    #     if find_file.find_files_with_existence(program_info.work_path + program_info.spigot_core_installation):
    #         log.logger.info('Spigot核心下载器已存在')
    #         return True
    #     else:
    #         try:
    #             log.logger.warning('Fabric核心下载器不存在')
    #             log.logger.info('正在下载Fabric核心下载器...')
    #             os.system('powershell curl -o '+ program_info.work_path + program_info.spigot_core_installation + ' https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.exe')
    #             log.logger.info('下载完成')
    #             return True
    #         except Exception as e:
    #             log.logger.error('获取Fabric核心下载器失败,请检查')
>>>>>>> 6c0b95ef8a36d5d56bb1e47e255c35b967a128a8
    #             return False