from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from bin.export import Info
from bin.export import Examine
from bin.command import Server
from bin.export import Get
from bin.export import log
import os

class Excel:
    """
    一个Excel处理类
    通过访问
    """
    class SignalSheet:
        """
        单工作表处理类
        用于输出单个服务器的信息
        参数：
        sheet: 工作表名称
        ServerInfo: 服务器信息

        方法：
        Method GenerateFile()
        用于生成Excel文件

        Method WriteData()
        用于写入数据

        Method FilePath()
        返回文件路径
        """
        def __init__(self, sheet, ServerInfo: list):
            self.sheet = sheet
            self.ServerInfo = ServerInfo
            self.wb1 = Workbook()  # 初始化工作簿对象

        def GenerateFile(self):
            """
            生成文件
            """
            # 确保每次生成文件时都是全新的工作簿
            self.wb1.active.title = self.sheet # 设置工作表名称
            self.wb1.create_sheet('存储变化数据')  # 创建第二个工作表

            self.wb1.save(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")

        def Auto_Adapt(self):
            """
            自动调整行宽和列高
            遍历查找所有工作表的所有单元格，找到最大长度的单元格，根据其长度调整列宽
            遍历查找所有工作表的所有单元格，找到最大长度的单元格，根据其长度调整行高
            """
            wb = load_workbook(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")
            ws = wb.active # 获取默认工作表
            max_row = ws.max_row
            max_col = ws.max_column

            for j in range(1, max_col + 1):
                max_d = 1
                for i in range(1, max_row + 1):
                    cell_value = ws.cell(i,j).value
                    if isinstance(cell_value,str):
                        d = len(cell_value.encode('utf-8'))
                    else:
                        d = len(str(cell_value))

                    if d > max_d:
                        max_d = d

                log.Debug(f'列{get_column_letter(j)}最大长度为{max_d}，调整为{max_d}')
                k = get_column_letter(j)
                ws.column_dimensions[k].width = max_d

            wb.save(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")

        def WriteData(self):
            """
            写入数据
            将服务器信息写入Excel文件
            """
            self.wb1 = load_workbook(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")
            self.ws1 = self.wb1.active # 获取默认工作表
            self.ws2 = self.wb1['存储变化数据']  # 获取第二个工作表

            HistoryPlayers = Server.Get.HistoryPlayers(self.ServerInfo)
            WhiteListPlayers = Server.Get.WhiteList(self.ServerInfo)
            if not isinstance(WhiteListPlayers, list):
                WhiteListPlayers = []
            BannedPlayers = Server.Get.BannedPlayers(self.ServerInfo)
            CurrentPlayers = Server.Get.CurrentPlayers(self.ServerInfo)
            if not isinstance(CurrentPlayers, list):
                CurrentPlayers = []
            else:
                CurrentPlayers = CurrentPlayers[2]

            StorageInfo = Get.Info.StorageSize(self.ServerInfo['Name'])
            if StorageInfo is None or not isinstance(StorageInfo, dict):
                StorageInfo = {'storage_size': [], 'time': []}

            # 标题行
            self.ws1['A1'] = '服务器名称'
            self.ws1['A2'] = '服务器版本号'
            self.ws1['A3'] = '核心类型'
            self.ws1['A4'] = '上次启动时间'
            self.ws1['A5'] = '启动次数'
            self.ws1['A6'] = '存储占用'
            self.ws1['A7'] = '历史玩家'
            self.ws1['A8'] = '白名单玩家'
            self.ws1['A9'] = '封禁玩家'
            self.ws1['A10'] = '当前玩家'

            # 写入服务器信息
            self.ws1['B1'] = self.ServerInfo['Name']
            self.ws1['B2'] = self.ServerInfo['Version']
            self.ws1['B3'] = self.ServerInfo['CoreType']
            self.ws1['B4'] = self.ServerInfo['LatestStartedTime']
            self.ws1['B5'] = self.ServerInfo['Counts']
            self.ws1['B6'] = self.ServerInfo['Size']
            self.ws1['B7'] = f'共{len(HistoryPlayers)}人'
            self.ws1['B8'] = f'共{len(WhiteListPlayers)}人'
            self.ws1['B9'] = f'共{len(BannedPlayers)}人'
            self.ws1['B10'] = f'共{len(CurrentPlayers)}人'
            for i in range(len(HistoryPlayers)):
                log.Debug(f'正在写入历史玩家 {HistoryPlayers[i]}')
                word = chr(67 + i)
                self.ws1[word + '7'] = HistoryPlayers[i]
            for i in range(len(WhiteListPlayers)):
                log.Debug(f'正在写入白名单玩家 {WhiteListPlayers[i]}')
                word = chr(67 + i)
                self.ws1[word + '8'] = WhiteListPlayers[i]
            for i in range(len(BannedPlayers)):
                log.Debug(f'正在写入封禁玩家 {BannedPlayers[i]}')
                word = chr(67 + i)
                self.ws1[word + '9'] = BannedPlayers[i]
            for i in range(len(CurrentPlayers)):
                log.Debug(f'正在写入当前玩家 {CurrentPlayers[i]}')
                word = chr(67 + i)
                self.ws1[word + '10'] = CurrentPlayers[i]


            # 写入第二个工作表
            self.ws2['A1'] = '存储占用'
            self.ws2['B1'] = '时间'

            # 写入存储占用数据
            if len(StorageInfo['storage_size']) == 0:
                self.ws2['A2'] = '无存储占用数据'
            else:
                for i in range(len(StorageInfo['storage_size'])):
                    self.ws2[f'A{i+2}'] = StorageInfo['storage_size'][i]
                    self.ws2[f'B{i+2}'] = StorageInfo['time'][i]

            # 保存文件
            self.wb1.save(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")

            self.Auto_Adapt()

        def FilePath(self):
                """
                返回文件路径
                """
                # 获取绝对路径
                AbsolutePath = os.path.abspath(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{self.sheet}.xlsx")

                return AbsolutePath

    class MultiSheet:
        """
        多工作表处理类
        用于输出多个服务器的信息
        参数：
        sheet: 工作表名称 -> 列表

        方法：
        Method GenerateFile()
        用于生成Excel文件

        Method WriteData()
        用于写入数据

        Method FilePath()
        返回文件路径
        """
        def __init__(self, sheets: list):
            self.sheets = sheets
            self.wb2 = Workbook()

        def GenerateFile(self):
            """
            生成文件
            """
            self.wb2.active.title = self.sheets[0] # 设置第一个工作表名称

            # 创建剩余的工作表
            for Name in self.sheets[1:]: # 从第二个名称开始
                self.wb2.create_sheet(title=Name)

            # 保存文件
            self.wb2.save(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{Info.File.Document.ServerInfoExcel}")

        def Auto_Adapt(self):
            """
            自动调整行宽和列高
            遍历查找所有工作表的所有单元格，找到最大长度的单元格，根据其长度调整列宽
            遍历查找所有工作表的所有单元格，找到最大长度的单元格，根据其长度调整行高
            """
            for sheet_name in self.sheets:
                self.ws2 = self.wb2[sheet_name]
                max_row = self.ws2.max_row
                max_col = self.ws2.max_column

                for j in range(1, max_col + 1):
                    max_d = 1
                    for i in range(1, max_row + 1):
                        cell_value = self.ws2.cell(i,j).value
                        if isinstance(cell_value,str):
                            d = len(cell_value.encode('utf-8'))
                        else:
                            d = len(str(cell_value))
                        if d > max_d:
                            max_d = d
                    log.Debug(f'列{get_column_letter(j)}最大长度为{max_d}，调整为{max_d}')
                    k = get_column_letter(j)
                    self.ws2.column_dimensions[k].width = max_d

        def WriteData(self):
            """
            写入数据
            将服务器信息写入Excel文件
            """
            self.wb2 = load_workbook(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{Info.File.Document.ServerInfoExcel}")

            for sheet_name in self.sheets:
                self.ws2 = self.wb2[sheet_name]

                ServerInfo = Server.Get.Search(sheet_name, False)
                if ServerInfo == None:
                    ServerInfo = {}

                HistoryPlayers = Server.Get.HistoryPlayers(ServerInfo)
                WhiteListPlayers = Server.Get.WhiteList(ServerInfo)
                if not isinstance(WhiteListPlayers, list):
                    WhiteListPlayers = []
                BannedPlayers = Server.Get.BannedPlayers(ServerInfo)
                CurrentPlayers = Server.Get.CurrentPlayers(ServerInfo)
                if not isinstance(CurrentPlayers, list):
                    CurrentPlayers = []
                else:
                    CurrentPlayers = CurrentPlayers[2]

                StorageInfo = Get.Info.StorageSize(ServerInfo['Name'])
                if StorageInfo == None or not isinstance(StorageInfo, dict):
                    StorageInfo = {'storage_size': [], 'time': []}

                # 标题行
                self.ws2['A1'] = '服务器名称'
                self.ws2['A2'] = '服务器版本号'
                self.ws2['A3'] = '核心类型'
                self.ws2['A4'] = '上次启动时间'
                self.ws2['A5'] = '启动次数'
                self.ws2['A6'] = '存储占用'
                self.ws2['A7'] = '历史玩家'
                self.ws2['A8'] = '白名单玩家'
                self.ws2['A9'] = '封禁玩家'
                self.ws2['A10'] = '当前玩家'

                # 获取服务器列表
                self.ServerInfo = Examine.Server.InfoKeys(sheet_name)

                # 写入服务器信息
                self.ws2['B1'] = ServerInfo['Name']
                self.ws2['B2'] = ServerInfo['Version']
                self.ws2['B3'] = ServerInfo['CoreType']
                self.ws2['B4'] = ServerInfo['LatestStartedTime']
                self.ws2['B5'] = ServerInfo['Counts']
                self.ws2['B6'] = ServerInfo['Size']
                self.ws2['B7'] = f'共{len(HistoryPlayers)}人'
                self.ws2['B8'] = f'共{len(WhiteListPlayers)}人'
                self.ws2['B9'] = f'共{len(BannedPlayers)}人'
                self.ws2['B10'] = f'共{len(CurrentPlayers)}人'
                for i in range(len(HistoryPlayers)):
                    word = chr(67 + i)
                    self.ws2[word + '7'] = HistoryPlayers[i]
                for i in range(len(WhiteListPlayers)):
                    word = chr(67 + i)
                    self.ws2[word + '8'] = WhiteListPlayers[i]
                for i in range(len(BannedPlayers)):
                    word = chr(67 + i)
                    self.ws2[word + '9'] = BannedPlayers[i]
                for i in range(len(CurrentPlayers)):
                    word = chr(67 + i)
                    self.ws2[word + '10'] = CurrentPlayers[i]

                self.ws2['A11'] = '存储占用'
                self.ws2['B11'] = '时间'

                if len(StorageInfo['storage_size']) == 0:
                    self.ws2['A12'] = '无存储占用数据'
                else:
                    for i in range(len(StorageInfo['storage_size'])):
                        self.ws2[f'A{i+12}'] = StorageInfo['storage_size'][i]
                        self.ws2[f'B{i+12}'] = StorageInfo['time'][i]

            self.Auto_Adapt()

            self.wb2.save(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{Info.File.Document.ServerInfoExcel}")

        def FilePath(self):
            """
            返回文件路径
            """
            # 获取绝对路径
            AbsolutePath = os.path.abspath(f"./{Info.File.Folder.Resource}/{Info.File.Folder.Excel}/{Info.File.Document.ServerInfoExcel}")

            return AbsolutePath