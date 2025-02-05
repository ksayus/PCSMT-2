import requests
import json
import urllib3
from bin.export import log

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