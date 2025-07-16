import requests
import json
import os
from bin.export import log
from bin.find_files import find_file

class Info:
    def MinecraftVersion():
        """
        获取Minecraft所有版本
        :return: Minecraft所有版本
        """
        log.logger.info("获取Minecraft版本...")
        version_list = []
        try:
            # 增加超时和状态码检查
            response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json', timeout=10)

            # 检查HTTP状态码
            if response.status_code != 200:
                log.logger.error(f"HTTP请求失败，状态码: {response.status_code}")
                return

            # 单独捕获JSON解析异常
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                log.logger.error(f"JSON解析失败: {e}")
                log.logger.error(f"响应内容: {response.text[:100]}...")  # 记录部分响应内容
                return

            for version in data["versions"]:
                version_list.append(version["id"])

            # 使用绝对路径读取配置
            config_path = os.path.join(os.getcwd(), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try:
                        config_read = json.load(f)
                        minecraft_test = config_read.get('Minecraft_Test_Version', "false")
                    except json.JSONDecodeError:
                        log.Debug("配置文件格式错误，使用默认值")
                        minecraft_test = "false"
            else:
                minecraft_test = "false"
                log.logger.warning("配置文件不存在，使用默认值")

            if minecraft_test.lower() == "false":
                exclude_keyword = {
                    'w', 'a', 'b', 'c', 'rd', 'rc', 'craftmine', 'inf', 'pre',
                    '1.RV-Pre1', '3D', 'Shareware', 'Pre-release',
                }
                version_list = [
                    item for item in version_list
                    if not any(keyword in item for keyword in exclude_keyword)
                ]

            log.Debug('Minecraft版本:' + json.dumps(version_list))
            return version_list

        except requests.exceptions.Timeout:
            log.logger.error("请求超时，请检查网络连接")
            return
        except requests.exceptions.RequestException as e:
            log.logger.error(f"网络请求失败: {e}")
            return
        except Exception as e:
            log.logger.error(f"获取Minecraft版本失败: {e}")
            return

    def PropertiesKeys():
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

    def DirSize(path):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += Info.DirSize(entry.path)
        return total

    def StorageSize(server_name):
        # 延迟导入 program_info，避免循环导入问题
        from bin.export import Info

        if find_file.find_files_with_existence(Info.work_path + Info.File.Folder.ServerStorageSize + '/' + f'{server_name}.json'):
            with open(Info.work_path + Info.File.Folder.ServerStorageSize + '/' + f'{server_name}.json', 'r', encoding='utf-8') as f:
                server_storage_size = json.load(f)
                return server_storage_size