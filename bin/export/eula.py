from bin.export import program_info
from bin.export import log

def examine_eula(server_info):
    try:
        with open(server_info['server_path'] + program_info.server_eula, 'r') as f:
            lines = f.readlines()
        with open(server_info['server_path'] + program_info.server_eula, 'w') as f:
            for line in lines:
                if 'eula=true' in line:
                    log.logger.info('eula协议已同意')
                    server_info['start_count'] += 1
                    break
                if 'eula=false' in line:
                    f.write('eula=true')
                    log.logger.info('已自动同意eula协议')
                    server_info['start_count'] += 1
                    break
                else:
                    f.write(line)
                    continue
        return server_info
    except Exception as e:
        log.logger.error('eula协议检查失败，请手动同意eula协议后重试')
        log.logger.error(e)
        server_info['start_count'] += 1
        return server_info