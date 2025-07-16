from bin.export import log
from bin.export import Info
from bin.find_files import find_folder
from bin.find_files  import find_file
from bin.export import size_change
from bin.export import Get
from bin.export import GetTime
from bin.command import Server
from bin.export import Examine
from bin.export import RCON
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
            if find_file.find_files_with_existence(Info.work_path + Info.File.Folder.Save + '/' + f'{server_name}.json'):
                server_info = Examine.Server.InfoKeys(server_name)

                if find_folder.find_folders_with_existence_and_create(Info.work_path + Info.File.Folder.ServerStorageSize):
                    if find_file.find_files_with_existence_and_create(Info.work_path + Info.File.Folder.ServerStorageSize + '/' + f'{server_name}.json'):
                        with open(Info.work_path + Info.File.Folder.ServerStorageSize + '/' + f'{server_name}.json', 'r', encoding='utf-8') as f:
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

                            StorageSize = size_change.size_change(Get.Info.DirSize(server_info['Path']))
                            NowTime = GetTime.TimeString.Auto_Time()

                            # 判断是否与上次的存储大小一致
                            # 先处理初次启动的情况
                            with open(Info.work_path + './config.json', 'r', encoding='utf-8') as f:
                                config_read = json.load(f)
                            StorageSizeUpdateTime = config_read['StorageSizeUpdateTime']

                            if StorageSizeUpdateTime > 0 and StorageSizeUpdateTime < 1555200: # 小于18天时启用
                                if server_save_json['storage_size'][-1] == StorageSize:
                                    log.Debug('存储大小无变化，不进行更新！')
                                    return

                            server_save_json['storage_size'].append(StorageSize)
                            server_save_json['time'].append(NowTime)
                        with open(Info.work_path + Info.File.Folder.ServerStorageSize + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
                            json.dump(server_save_json, f, indent=4)

                        # 写入服务器信息文件
                        with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
                            server_info = json.load(f)
                            with open(Info.work_path + Info.File.Folder.Save + '/' + server_name + '.json', 'w', encoding='utf-8') as f:
                                # 写入文件
                                server_info['server_size'] = server_save_json['storage_size'][-1]

                                json.dump(server_info, f, indent=4)

        except Exception as e:
            log.logging.error(f'{server_name}服务器存储空间更新失败！')
            log.logging.error(e)
            return

    def timer(self, server_name):
        while True:
            if find_file.find_files_with_existence(Info.work_path + Info.File.Document.Config):
                with open(Info.work_path + Info.File.Document.Config, 'r', encoding='utf-8') as f:
                    config_read = json.load(f)
            a_loop = config_read['StorageSizeUpdateTime']
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
        """
        启动定时器
        此函数为此类的入口函数，用于启动定时器
        """
        TimerStorageSizeUpdate.StopTimerStorageSizeUpdate.clear()

        if Info.Information.ServerList is not None:
            # 为每一个服务器创建定时任务
            # 每个定时任务都单独为一个线程
            server_timer_thread = []  # 初始化为空列表
            i = 0
            for server in Info.Information.ServerList:
                i += 1
                # 创建Timer实例并正确传递参数
                timer_instance = TimerStorageSizeUpdate()
                server_timer_thread.append(threading.Thread(target=timer_instance.start_timer, args=(server,), daemon=True))

            # 确保线程对象正确启动
            for thread in server_timer_thread:
                thread.start()

class Heartbeat:
    WaitTime = threading.Event()
    List = {}
    def __init__(self):
        self.Frequency = 4

    def thread(self):
        HeartbeatInstance = Heartbeat()
        self.body = threading.Thread(target=HeartbeatInstance.Start, daemon=True)
        self.body.start()

    def Start(self):
        Temp = self.Frequency
        while Temp:
            Heartbeat.WaitTime.wait(self.Frequency)
            self.GetInfo()

    def GetInfo(self):
        # 将self.List从列表改为字典
        self.List = {'Name': [], 'Online': []}
        list = Server.Get.List(ShowMessage=False)
        if list is None: return
        for server in list:
            try:
                ServerInfo = Examine.Server.InfoKeys(server)
                # 向字典的Name列表添加服务器名称
                self.List['Name'].append(Server.Get.Search(server, Output=False)['Name'])
                # 向字典的Online列表添加服务器在线状态
                self.List['Online'].append(RCON.Infomation.ServerOnline(ServerInfo))
            except Exception as e:
                log.logger.error("获取失败")
                log.logger.error(e)
        # print(self.List)