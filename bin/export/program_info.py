import os
import json
from bin.command import server
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log
from bin.export import init
from bin.export import get

program_name = 'PCSMT2'

server_start_batch = '\start.bat'
server_save_path = '\saves'
server_storage_size = '\server_storage_size'
server_eula = '\eula.txt'
program_logs = '\logs'
server_properties = '\server.properties'
program_config = '\config.json'
server_mods_folder = '\mods'
server_plugins_folder = '\plugins'
program_server_folder = '\servers'
delete_old_program = '\delete_old_program.bat'
program_resource = '/resource'
resource_core_installation = '/core_installation'
latest_start_server = '/latest.txt'
latest_start_server_json = '/latest.json'

banned_player = '/banned-players.json'
banned_ip = '/banned-ips.json'
op = '/ops.json'
eula = '/eula.txt'

forge_server_start_batch_default_name = '/run.bat'
forge_server_JVM_args = '@user_jvm_args.txt'

# Debug
fabric_core_installation = '/bin/source/core_installation/fabric-installer.jar'
forge_core_installation = '/bin/source/core_installation/forge-installer.jar'
spigot_core_installation = '/bin/source/core_installation/spigot-installer.exe'

# Release
fabric_core_installation_save = '/resource/core_installation/fabric-installer.jar'
forge_core_installation_save = '/resource/core_installation/forge-installer.jar'
spigot_core_installation_save = '/resource/core_installation/spigot-installer.exe'

fabric_core_default_name = '/fabric-server-launch.jar'
forge_core_default_name = '/forge-installer.jar'
official_core_default_name = '/official-server.jar'
mohist_core_default_name = '/mohist-server.jar'

github_repository = "https://api.github.com/repos/ksayus/PCSMT-2/releases/latest"
gitee_repository = "https://gitee.com/api/v5/repos/ksayus/PCSMT-2/releases/latest?access_token=7a91263148087aa5e2c9447297fa04b1"

rcon_password = 'pcsmt2'
rcon_localhost = 'localhost'

work_path = os.getcwd()

server_list = server.server_list()
minecraft_version = get.get_minecraft_version()
properties_keyword = get.get_properties_keyword()


banned_players ={
    "uuid": "",
    "name": "",
    "created": "",
    "source": "PCSMT-2",
    "expires": "forever",
    "reason": "Banned by PCSMT-2"
}

banned_ips = {
    "ip": "",
    "created": "",
    "source": "PCSMT-2",
    "expires": "forever",
    "reason": "Banned by PCSMT-2"
}

ops = {
    "uuid": "",
    "name": "",
    "level": 4,
    "bypassesPlayerLimit": False
}

config = {
            "PCSMTVersion": "1.1.8",
            "Release_Version": "Release",
            "default_server_run_memories_min": 1024,
            "default_server_run_memories_max": 2048,
            "server_start_nogui": True,
            "wait_server_eula_generate_time": 15,
            "Automatic_startup": True,
            "Auto_Update_Source": "Github",
            "Minecraft_Test_Version": False
}

program_config_read = {
    "PCSMTVersion": "",
    "Release_Version": "",
    "default_server_run_memories_min": 0,
    "default_server_run_memories_max": 0,
    "server_start_nogui": False,
    "wait_server_eula_generate_time": 0,
    "Automatic_startup": False,
    "Auto_Update_Source": "",
    "Minecraft_Test_Version": False
}

program_config_read = init.read_config_json()

PCSMTVersion = program_config_read['PCSMTVersion']
Release_Version = program_config_read['Release_Version']
default_server_run_memories_min = program_config_read['default_server_run_memories_min']
default_server_run_memories_max = program_config_read['default_server_run_memories_max']
server_start_nogui = program_config_read['server_start_nogui']
wait_server_eula_generate_time = program_config_read['wait_server_eula_generate_time']
Automatic_startup = program_config_read['Automatic_startup']
Auto_Update_Source = program_config_read['Auto_Update_Source']
Minecraft_Test_Version = program_config_read['Minecraft_Test_Version']