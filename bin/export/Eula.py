from bin.export import Info
from bin.export import log

class Examine:
    def IsAgree(server_info):
        """
        检查eula协议
        :param server_info: 服务器信息
        """
        try:
            with open(server_info['Path'] + Info.File.Document.Eula, 'r') as f:
                lines = f.readlines()
            with open(server_info['Path'] + Info.File.Document.Eula, 'w') as f:
                for line in lines:
                    if 'eula=true' in line:
                        f.write(line)
                        log.logger.info('eula协议已同意')
                        break
                    if 'eula=false' in line:
                        f.write('eula=true')
                        log.logger.info('已自动同意eula协议')
                        server_info['Counts'] += 1
                        break
                    else:
                        f.write(line)
                        continue
            return server_info
        except Exception as e:
            log.logger.error('eula协议检查失败，请手动同意eula协议后重试')
            log.logger.error(e)
            server_info['Counts'] += 1
            return server_info