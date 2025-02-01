import os
import json
from bin.find_files import find_file
from bin.find_files import find_folder
from bin.export import log
from bin.export import init

server_start_batch = '\start.bat'
server_save_path = '\saves'
server_eula = '\eula.txt'
program_logs = '\logs'
server_properties = '\server.properties'
program_config = '\config.json'
server_mods_folder = '\mods'
server_plugins_folder = '\plugins'
program_server_folder = '\servers'

forge_server_start_batch_default_name = '/run.bat'
forge_server_JVM_args = '@user_jvm_args.txt'

fabric_core_installation = '/bin/source/core_installation/fabric-installer.jar'
forge_core_installation = '/bin/source/core_installation/forge-installer.jar'
spigot_core_installation = '/bin/source/core_installation/spigot-installer.exe'

fabric_core_default_name = '/fabric-server-launch.jar'
forge_core_default_name = '/forge-installer.jar'
official_core_default_name = '/official-server.jar'
mohist_core_default_name = '/mohist-server.jar'

work_path = os.getcwd()

config = {
            "PCSMTVersion": "1.0.2",
            "default_server_run_memories_min": 1024,
            "default_server_run_memories_max": 2048,
            "server_start_nogui": True
}

program_config_read = {
    "PCSMTVersion": "",
    "default_server_run_memories_min": 0,
    "default_server_run_memories_max": 0,
    "server_start_nogui": False
}

program_config_read = init.read_config_json()

PCSMTVersion = program_config_read['PCSMTVersion']
default_server_run_memories_min = program_config_read['default_server_run_memories_min']
default_server_run_memories_max = program_config_read['default_server_run_memories_max']
server_start_nogui = program_config_read['server_start_nogui']