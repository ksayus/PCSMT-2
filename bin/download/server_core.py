from bin.export import program_info
from bin.export import log
from bin.download import core_installer
from pathlib import Path
import os
import requests
import time

def download_server_core(server_name, core_type, core_support_version):
    """
    下载服务器核心
    :param server_name: 服务器名称
    :param core_type: 核心类型
    :param core_support_version: 核心支持版本
    :return: bool
    """
    #fabric核心
    if core_type == 'fabric':
        if core_installer.init_core_installer(core_type, core_support_version):
            time.sleep(3)
            try:
                log.logger.info('正在下载Fabric核心...')
                os.system('powershell java -jar ' + program_info.work_path + program_info.fabric_core_installation + ' server -mcversion ' + core_support_version + ' -downloadMinecraft -dir "' + program_info.work_path + program_info.program_server_folder + '\\' + server_name + '"')
                core_path_default = Path(program_info.work_path + program_info.program_server_folder + '\\' + server_name + program_info.fabric_core_default_name)
                if core_path_default.exists():
                    core_path_default.rename(program_info.work_path + program_info.program_server_folder + '\\' + server_name + '\\' + server_name + '.jar')
                    log.logger.info('下载Fabric核心成功')
                    #os.remove(program_info.work_path + program_info.fabric_core_installation)
                    return True
            except Exception as e:
                log.logger.error('下载Fabric核心失败,请检查')
                log.logger.error(e)
                return False

    #forge下载网址示例
    #https://maven.minecraftforge.net/net/minecraftforge/forge/1.16.5-36.2.42/forge-1.16.5-36.2.42-installer.jar
    #version api
    #https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json

    #forge核心
    if core_type == 'forge':
        if core_installer.init_core_installer(core_type, core_support_version):
            time.sleep(3)
            try:
                log.logger.info('正在下载Forge核心...')
                os.system('java -jar ' + program_info.work_path + program_info.forge_core_installation + ' --installServer "' + program_info.work_path + program_info.program_server_folder + '\\' + server_name + '"')
                os.remove(program_info.work_path + program_info.forge_core_installation)
                log.logger.info('下载Forge核心成功')
                return True
            except Exception as e:
                log.logger.error('下载Forge核心失败,请检查')
                log.logger.error(e)
                return False

    #官方核心
    if core_type == 'official':
        try:
            version_manifest = requests.get('https://piston-meta.mojang.com/mc/game/version_manifest_v2.json').json()
            version_info = next(version for version in version_manifest['versions'] if version['id'] == core_support_version)
            version_details = requests.get(version_info['url']).json()
            server_download_url = version_details['downloads']['server']['url']
            log.logger.info('正在下载官方核心...')
            log.logger.info('当前下载链接:' + server_download_url)
            os.system('powershell curl -o '+ program_info.work_path + program_info.program_server_folder + '\\' + server_name + program_info.official_core_default_name + ' ' + server_download_url)
            log.logger.info('下载官方核心成功')
            return True
        except Exception as e:
            log.logger.error('下载官方核心失败,请检查')
            log.logger.error(e)
            return False

    #mohist核心
    if core_type == 'mohist':
        try:
            version_manifest = requests.get('https://mohistmc.com/api/v2/projects/mohist/' + core_support_version + '/builds').json()
            version_builds = version_manifest['builds']
            version_info = version_builds[-1]
            server_download_url = version_info['url']
            log.logger.info('正在下载Mohist核心...')
            log.logger.info('当前下载链接:' + server_download_url)
            os.system('powershell curl -o '+ program_info.work_path + program_info.program_server_folder + '\\' + server_name + program_info.mohist_core_default_name + ' ' + server_download_url)
            return True
        except Exception as e:
            log.logger.error('下载Mohist核心失败,请检查')
            log.logger.error(e)
            return False

    # if core_type == 'spigot':
    #     if core_installer.init_core_installer(core_type, core_support_version):
    #         time.sleep(3)
    #         try:
    #             log.logger.info('正在下载Spigot核心...')
    #             os.system('cd ' + program_info.work_path + program_info.program_server_folder + '\\' + server_name)
    #             os.system('java -Djavax.net.ssl.trustStore="C:\Program Files\Java\jdk-21\lib\security\cacerts" -jar ' + program_info.work_path + program_info.spigot_core_installation + ' --rev  ' + core_support_version)
    #             log.logger.info('下载Spigot核心成功')
    #             return True
    #         except Exception as e:
    #             log.logger.error('下载Spigot核心失败,请检查')
    #             log.logger.error(e)
    #             return False

    log.logger.error('输入的核心类型不正确，请检查输入')