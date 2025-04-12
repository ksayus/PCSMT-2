from bin.export import program_info
from bin.export import log
from bin.find_files import find_file
import mcrcon
import requests

def set_rcon(server_info):
    try:
        with open(server_info['server_path'] + program_info.server_properties, 'r', encoding='utf-8') as f:
            log.logger.info('正在获取服务器端口...')
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

            log.logger.info('正在开启RCON...')
            find_file.find_keyword_inline_and_change_argument(server_info['server_path'] + program_info.server_properties, 'enable-rcon', 'true')
            log.logger.info('正在设置RCON端口...')
            find_file.find_keyword_inline_and_change_argument(server_info['server_path'] + program_info.server_properties, 'rcon.port', str(port))
            log.logger.info('正在设置RCON密码...')
            find_file.find_keyword_inline_and_change_argument(server_info['server_path'] + program_info.server_properties, 'rcon.password', program_info.rcon_password)

            return port
    except Exception as e:
        log.logger.error('修改服务器属性失败！')
        log.logger.error(e)
        return

def connect_rcon(port):
    try:
        log.logger.info('正在连接RCON...')
        # 确保端口是整数并且在合理范围内
        if not (0 <= port <= 65535):
            log.logger.error(f'无效的端口号: {port}')

        with mcrcon.MCRcon(program_info.rcon_localhost, program_info.rcon_password, port) as mcr:
            response = mcr.command("/say Hello from RCON! I'm PCSMT2!")
            log.logger.info("Server response: %s", response)
        log.logger.info('连接RCON成功！')
        return mcr
    except Exception as e:
        log.logger.error('连接RCON失败！')
        log.logger.error(e)
        return

def rcon_port(server_info):
    try:
        with open(server_info['server_path'] + program_info.server_properties, 'r', encoding='utf-8') as f:
            log.logger.info('正在获取rcon端口...')
            lines = f.readlines()
            matched_lines = []
            for line_number, line in enumerate(lines, start=1):
                if 'rcon.port' in line:
                    matched_lines.append((line_number, line))
                    port = int(lines[line_number - 1].split('=')[1].strip())
                    return port
    except Exception as e:
        log.logger.error('获取rcon端口失败！')
        log.logger.error(e)
        return