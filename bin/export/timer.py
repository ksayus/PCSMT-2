from bin.export import log
from bin.export import program_info
from bin.find_files import find_folder
from bin.find_files  import find_file
from bin.export import size_change
from bin.export import get
from bin.export import get_time
import json
import threading

class TimerStorageSizeUpdate:
    # global variables
    StopTimerStorageSizeUpdate = threading.Event()

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

                            # 写入服务器信息文件
                            with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                                server_info = json.load(f)
                                with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
                                    # 写入文件
                                    server_info['server_size'] = server_save_json['storage_size'][-1]

                                    json.dump(server_info, f, indent=4)

        except Exception as e:
            log.logging.error(f'{server_name}服务器存储空间更新失败！')
            log.logging.error(e)
            return

    def timer(self, server_name):
        while True:
            if find_file.find_files_with_existence(program_info.work_path + program_info.program_config):
                with open(program_info.work_path + program_info.program_config, 'r', encoding='utf-8') as f:
                    config_read = json.load(f)
            a_loop = config_read['Storage_Size_Update_Time']
            while a_loop > 0:
                # 保证线程随时可中断
                if TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.is_set():
                    break
                TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.wait(1)
                a_loop -= 1
            if TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.is_set():
                    break
            TimerStorageSizeUpdate.every_time_update_server_storage_size(self, server_name)
    @classmethod  # 添加类方法装饰器
    def thread(cls):  # 修改第一个参数为cls
        TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.clear()

        if program_info.server_list is not None:
            # 为每一个服务器创建定时任务
            # 每个定时任务都单独为一个线程
            server_timer_thread = []  # 初始化为空列表
            i = 0
            for server in program_info.server_list:
                i += 1
                # 创建Timer实例并正确传递参数
                timer_instance = TimerStorageSizeUpdate()
                server_timer_thread.append(threading.Thread(target=timer_instance.start_timer, args=(server,), daemon=True))

            # 确保线程对象正确启动
            for thread in server_timer_thread:
                thread.start()