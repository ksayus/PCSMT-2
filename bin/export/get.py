import requests
import json
import os
from bin.export import log
from bin.export import program_info
from bin.find_files import find_file

def get_minecraft_version():
    """
    获取Minecraft所有版本
    :return: Minecraft所有版本
    """
    log.logger.info("获取Minecraft版本...")
    version_list = []
    try:
        response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
        for version in response.json()["versions"]:
            version_list.append(version["id"])
        if len(version_list) > 1:
            with open("./config.json", 'r', encoding='utf-8') as f:
                config_read = json.load(f)

            for i in range(len(version_list)):
                if config_read['Minecraft_Test_Version'] == "false":
                    exclude_keyword = {
                        'w',
                        'a',
                        'b',
                        'c',
                        'rd',
                        'rc',
                        'craftmine',
                        'inf',
                        'pre',
                        '1.RV-Pre1',
                        '3D',
                        'Shareware',
                        'Pre-release',
                    }

                    version_list = [
                        item for item in version_list
                        if not any(keyword in item for keyword in exclude_keyword)
                    ]
        log.logger.debug('Minecraft版本:' + json.dumps(version_list))
        return version_list
    except Exception as e:
        log.logger.error("获取Minecraft版本失败，请检查网络连接！")
        log.logger.error(e)
        return

def get_properties_keyword():
    """
    获取Minecraft所有属性关键字
    :return: Minecraft所有属性关键字
    """
    keyword=[
        'allow-flight',
        'allow-nether',
        'broadcast-console-to-ops',
        'broadcast-rcon-to-ops',
        'difficulty',
        'enable-command-block',
        'enable-jmx-monitoring',
        'enable-query',
        'enable-rcon',
        'enable-status',
        'enforce-secure-profile',
        'enforce-whitelist',
        'entity-broadcast-range-percentage',
        'force-gamemode',
        'function-permission-level',
        'gamemode',
        'generate-structures',
        'generator-settings',
        'hardcore',
        'hide-online-players',
        'initial-disabled-packs',
        'initial-enabled-packs',
        'level-name',
        'level-seed',
        'level-type',
        'max-chained-neighbor-updates',
        'max-players',
        'max-tick-time',
        'max-world-size',
        'motd',
        'network-compression-threshold',
        'online-mode',
        'op-permission-level',
        'player-idle-timeout',
        'prevent-proxy-connections',
        'pvp',
        'query.port',
        'rate-limit',
        'rcon.password',
        'rcon.port',
        'require-resource-pack',
        'resource-pack',
        'resource-pack-prompt',
        'resource-pack-sha1',
        'server-ip',
        'server-port',
        'simulation-distance',
        'spawn-animals',
        'spawn-monsters',
        'spawn-npcs',
        'spawn-protection',
        'sync-chunk-writes',
        'text-filtering-config',
        'use-native-transport',
        'view-distance',
        'white-list'
    ]
    return keyword

def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

def get_server_storage_size(server_name):
    if find_file.find_files_with_existence(program_info.work_path + program_info.server_storage_size + '/' + f'{server_name}.json'):
        with  open(program_info.work_path + program_info.server_storage_size + '/' + f'{server_name}.json', 'r', encoding='utf-8') as f:
            server_storage_size = json.load(f)

            return server_storage_size