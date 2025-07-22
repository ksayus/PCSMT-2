import os
from bin.command import Server
from bin.export import Init
from bin.export import Get

program_name = 'PCSMT2'

class File:
    class Folder:
        Save = '\saves'
        ServerStorageSize = '\server_storage_size'
        Logs = '\logs'
        Mods = '\mods'
        Plugins = '\plugins'
        Servers = '\servers'
        Resource = '/resource'
        CoreInstallation = '/core_installation'
        Excel = '/excel'

    class Document:
        StartBatch = '\start.bat'
        Eula = '\eula.txt'
        ServerProperties = '\server.properties'
        Config = '\config.json'
        DeteleteOldProgram = '\delete_old_program.bat'
        Latest = '/latest.txt'
        Latest_json = '/latest.json'
        banned_player = '/banned-players.json'
        banned_ip = '/banned-ips.json'
        op = '/ops.json'
        ForgeServerStartBatchDefaultName = '/run.bat'
        ForgeServer_JVM_args = '@user_jvm_args.txt'
        ServerInfoExcel = '/AllServerInfo.xlsx'

class RCON:
    def LocalHost():
        return '127.0.0.1'
    def Password():
        return 'pcsmt2'


class Core:
    class Position:
        # Debug
        fabric_core_installation = '/bin/source/core_installation/fabric-installer.jar'
        forge_core_installation = '/bin/source/core_installation/forge-installer.jar'
        spigot_core_installation = '/bin/source/core_installation/spigot-installer.exe'

        # Release
        fabric_core_installation_save = '/resource/core_installation/fabric-installer.jar'
        forge_core_installation_save = '/resource/core_installation/forge-installer.jar'
        spigot_core_installation_save = '/resource/core_installation/spigot-installer.exe'
    class DefaultName:
        Fabric = '/fabric-server-launch.jar'
        Forge = '/forge-installer.jar'
        Official = '/official-server.jar'
        Mohist = '/mohist-server.jar'

class ProjectRepository:
    Github = "https://api.github.com/repos/ksayus/PCSMT-2/releases/latest"
    Gitee = "https://gitee.com/api/v5/repos/ksayus/PCSMT-2/releases/latest"

work_path = os.getcwd()

class Information:
    ServerList = Server.Get.List(ShowMessage=False)
    MinecraftVersion = Get.Info.MinecraftVersion()
    PropertiesKeys = Get.Info.PropertiesKeys()

class Config:
    _config_cache = None  # 添加配置缓存

    Config = {
        "PCSMT2_Version": "1.2.1",
        "ReleaseVersion": "Release",
        "RunningMemories_Min": 1024,
        "RunningMemories_Max": 2048,
        "Nogui": True,
        "WaitEulaGenerateTime": 30,
        "AutomaticStartup": True,
        "AutoUpdateSource": "Github",
        "MinecraftTestVersion": False,
        "StorageSizeUpdateTime": 3600,
        "Port": 5000
    }

    ConfigRead = {
        "PCSMT2_Version": str,
        "ReleaseVersion": str,
        "RunningMemories_Min": int,
        "RunningMemories_Max": int,
        "Nogui": bool,
        "WaitEulaGenerateTime": int,
        "AutomaticStartup": bool,
        "AutoUpdateSource": str,
        "MinecraftTestVersion": bool,
        "StorageSizeUpdateTime": int,
        "Port": int
    }

    @classmethod
    def _load_config(cls):
        """惰性加载配置，避免循环导入"""
        if cls._config_cache is None:
            try:
                from bin.export import Init
                cls._config_cache = Init.Infomation.Config()
            except Exception:
                # 回退到默认配置
                cls._config_cache = cls.Config.copy()
        return cls._config_cache

    @classmethod
    def PCSMT2_Version(cls):
        return cls._load_config().get('PCSMT2_Version', cls.Config['PCSMT2_Version'])

    # 为每个配置属性添加对应的访问方法
    @classmethod
    def ReleaseVersion(cls):
        return cls._load_config().get('ReleaseVersion', cls.Config['ReleaseVersion'])

    @classmethod
    def RunningMemories_Min(cls):
        return cls._load_config().get('RunningMemories_Min', cls.Config['RunningMemories_Min'])

    @classmethod
    def RunningMemories_Max(cls):
        return cls._load_config().get('RunningMemories_Max', cls.Config['RunningMemories_Max'])

    @classmethod
    def Nogui(cls):
        return cls._load_config().get('Nogui', cls.Config['Nogui'])

    @classmethod
    def WaitEulaGenerateTime(cls):
        return cls._load_config().get('WaitEulaGenerateTime', cls.Config['WaitEulaGenerateTime'])

    @classmethod
    def AutomaticStartup(cls):
        return cls._load_config().get('AutomaticStartup', cls.Config['AutomaticStartup'])

    @classmethod
    def AutoUpdateSource(cls):
        return cls._load_config().get('AutoUpdateSource', cls.Config['AutoUpdateSource'])

    @classmethod
    def MinecraftTestVersion(cls):
        return cls._load_config().get('MinecraftTestVersion', cls.Config['MinecraftTestVersion'])

    @classmethod
    def StorageSizeUpdateTime(cls):
        return cls._load_config().get('StorageSizeUpdateTime', cls.Config['StorageSizeUpdateTime'])

    @classmethod
    def Port(cls):
        return cls._load_config().get('Port', cls.Config['Port'])