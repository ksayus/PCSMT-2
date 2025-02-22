import json
from bin.export import program_info
from bin.export import log

def examin_saves_json_argument(server_name):
    """
    检查服务器信息json文件
    :param server_name: 服务器名称
    :return: False(错误) or server_info(正确)
    """
    try:
        with open(program_info.work_path + program_info.server_save_path + '/' + server_name + '.json', 'r', encoding='utf-8') as f:
            server_info = json.load(f)
            f.close()
            if not 'server_name' in server_info:
                log.logger.error('服务器信息文件缺少server_name字段！')
                return False
            if not 'start_count' in server_info:
                log.logger.error('服务器信息文件缺少start_count字段！')
                return False
            if not 'server_core' in server_info:
                log.logger.error('服务器信息文件缺少server_core字段！')
                return False
            if not 'server_path' in server_info:
                log.logger.error('服务器信息文件缺少server_path字段！')
                return False
            if not 'server_start_batch_path' in server_info:
                log.logger.error('服务器信息文件缺少server_start_batch_path字段！')
                return False
        return server_info
    except Exception as e:
        log.logger.error('读取服务器信息失败！')
        log.logger.error(e)
        return False