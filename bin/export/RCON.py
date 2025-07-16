from bin.export import Info
from bin.export import log
from bin.find_files import find_file
import mcrcon

class Set:
    def RCON(server_info):
        """
        设置RCON
        server_info: 服务器信息
        return: rcon端口
        """
        try:
            with open(server_info['Path'] + Info.File.Document.ServerProperties, 'r', encoding='utf-8') as f:
                log.Debug('正在获取服务器端口...')
                lines = f.readlines()
                matched_lines = []
                for line_number, line in enumerate(lines, start=1):
                    if 'server-port' in line:
                        matched_lines.append((line_number, line))
                        port = int(lines[line_number - 1].split('=')[1].strip()) + 10
                        if not (0 <= port <= 65535):
                            log.logger.error(f'无效的端口号: {port}')
                            log.logger.info('尝试切换rcon端口...')
                            port = int(lines[line_number - 1].split('=')[1].strip()) - 10
                            if not (0 <= port <= 65535):
                                log.logger.error(f'无效的端口号: {port}')
                                log.logger.info('请手动设置rcon端口！')
                                return

                log.Debug('正在开启RCON...')
                find_file.find_keyword_inline_and_change_argument(server_info['Path'] + Info.File.Document.ServerProperties, 'enable-rcon', 'true')
                log.Debug('正在设置RCON端口...')
                find_file.find_keyword_inline_and_change_argument(server_info['Path'] + Info.File.Document.ServerProperties, 'rcon.port', str(port))
                log.Debug('正在设置RCON密码...')
                find_file.find_keyword_inline_and_change_argument(server_info['Path'] + Info.File.Document.ServerProperties, 'rcon.password', Info.RCON.Password())

                return port
        except Exception as e:
            log.logger.error('修改服务器属性失败！')
            log.logger.error(e)
            return

class Get:
    def RCON_Object(port: int, msg=True):
        """
        连接RCON
        port: RCON端口
        return: RCON连接对象
        """
        try:
            log.Debug('正在连接RCON...')
            # 确保端口是整数并且在合理范围内
            if not (0 <= port <= 65535):
                log.logger.error(f'无效的端口号: {port}')
                return False

            log.Debug(f'正在连接: {port}')
            with mcrcon.MCRcon(Info.RCON.LocalHost(), Info.RCON.Password(), int(port)) as mcr:
                if msg:
                    response = mcr.command("/say Hello from RCON! I'm PCSMT2!")
                    log.Debug("Server response: %s", response)
            log.Debug('连接RCON成功！')
            return mcr
        except Exception as e:
            if msg:
                log.logger.error('连接RCON失败！')
                log.logger.error(e)
            return False

    def Port(ServerInfo, msg=True):
        """
        获取RCON端口
        ServerInfo: 服务器信息
        返回: RCON端口号
        """
        try:
            with open(ServerInfo['Path'] + Info.File.Document.ServerProperties, 'r', encoding='utf-8') as f:
                log.Debug('正在获取rcon端口...')
                lines = f.readlines()
                matched_lines = []
                for line_number, line in enumerate(lines, start=1):
                    if 'rcon.port' in line:
                        matched_lines.append((line_number, line))
                        port = int(lines[line_number - 1].split('=')[1].strip())
                        return port
        except Exception as e:
            if msg:
                log.logger.error('获取rcon端口失败！')
                log.logger.error(e)
            return

class Infomation:
    def ServerStatus(ServerInfo):
        """
        获取服务器状态
        通过RCON连接服务器以判断服务器是否已启动
        ServerInfo: 服务器信息
        return: True / False
        True: 服务器已启动
        False: 服务器未启动
        """
        try:
            log.logger.info('获取服务器状态')
            port = Get.Port(ServerInfo)
            try:
                if Get.RCON_Object(port) == False:
                    return False
                return True
            except Exception as e:
                log.logger.error('链接rcon失败!')
                log.logger.error(e)
                return False
        except Exception as e:
            log.logger.error('读取服务器信息文件失败！')
            log.logger.error(e)
            return False

    def ServerOnline(ServerInfo):
        """
        获取服务器在线信息
        通过RCON获取服务器在线信息
        然后通过分割信息获取在线玩家数量和最大玩家数量
        接着分割信息获取在线玩家列表
        最后返回在线玩家数量、最大玩家数量和在线玩家列表

        server_name: 服务器名称
        return: 在线玩家数量、最大玩家数量和在线玩家列表
        """
        try:
            port = Get.Port(ServerInfo, msg=False)
            rcon = Get.RCON_Object(port, msg=False)
            rcon.connect()
            Response = rcon.command('/list')
            Content = Response.split(' ')

            # 获取在线人数
            Player_Min = Content[2]
            # 获取最大人数
            Player_Max = Content[7]

            Players = Response.split(": ")[1]
            # 获取在线玩家列表
            Players_list = Players.split(", ")

            # msg = "当前服务器有 " + str(Player_Min) + " / " + str(Player_Max) + " 人在线" + "\n" + "在线玩家列表：" + "\n" + Players
            # log.Debug(msg)

            return [Player_Min, Player_Max, Players_list]
        except Exception:
            return False

    def EnableRCON(ServerInfo):
        """
        检查RCON是否启用
        ServerInfo: 服务器信息
        return: True / False
        True: RCON已启用
        False: RCON未启用
        """
        # 获取RCON端口开启状态
        try:
            with open(ServerInfo['Path'] + Info.File.Document.ServerProperties, 'r', encoding='utf-8') as f:
                log.logger.info('获取rcon开启状态...')
                lines = f.readlines()
                matched_lines = []
                for line_number, line in enumerate(lines, start=1):
                    if 'enable-rcon' in line:
                        matched_lines.append((line_number, line))
                        RCON_key = lines[line_number - 1].split('=')[1].strip()
                return RCON_key
        except Exception as e:
            log.logger.error('未找到服务器配置文件！')
            log.logger.error(e)
            return