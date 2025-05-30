from bin.command import program
from bin.export import log
from bin.export import program_info
from bin.find_files import find_folder
from bin.find_files  import find_file
from bin.export import size_change
from bin.export import get
from bin.export import get_time
import json
from time import sleep

class Timer:
 # 现在self是Timer实例
    def start_timer(self, server_name):  # 保持实例方法签名
        self.timer(server_name)

    def every_time_update_server_storage_size(self, server_name):
        try:
            if find_file.find_files_with_existence(program_info.work_path + program_info.server_save_path + '/' + f'{server_name}.json'):
                with open(program_info.work_path + program_info.server_save_path + '/' + f'{server_name}.json', 'r', encoding='utf-8') as f:
                    server_info = json.load(f)

                    if find_folder.find_folders_with_existence_and_create(program_info.work_path + program_info.server_storage_size):
                        if find_file.find_files_with_existence_and_create(program_info.work_path + program_info.server_storage_size + '/' + f'{server_name}.json'):
                            with open(program_info.work_path + program_info.server_storage_size + '/' + f'{server_name}.json', 'r', encoding='utf-8') as f:
                                try:
                                    server_save_json = json.load(f)
                                except json.decoder.JSONDecodeError:
                                    # 处理空文件情况
                                    server_save_json = {
                                        'storage_size': [],
                                        'time': []
                                    }

                                if not server_save_json:  # 补充空字典检查
                                    server_save_json = {
                                        'storage_size': [],
                                        'time': []
                                    }

                                server_save_json['storage_size'].append(size_change.size_change(get.get_dir_size(server_info['server_path'])))
                                server_save_json['time'].append(get_time.now_time_year_month_day_hour())
                            with open(program_info.work_path + program_info.server_storage_size + '/' + server_name + '.json', 'w', encoding='utf-8') as f:  
                                json.dump(server_save_json, f, indent=4)

        except Exception as e:
            log.logging.error(f'{server_name}服务器存储空间更新失败！')
            log.logging.error(e)
            return

    def timer(self, server_name):
        a_loop = 3600
        while True:
            sleep(a_loop)
            Timer.every_time_update_server_storage_size(self, server_name)

