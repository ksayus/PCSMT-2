<<<<<<< HEAD
import os
from bin.export import log

def start_file(file_path):
    """
    打开文件
    :param file_path: 文件路径
    """
    try:
        return_code = os.system("start " + file_path)
        if return_code == 0:
            log.logger.info('已打开文件：' + file_path)    
        else:
            log.logger.error('打开文件失败！')
    except Exception as e:
        log.logger.error('打开文件失败！')
        log.logger.error(e)
=======
import os
from bin.export import log

def start_file(file_path):
    """
    打开文件
    :param file_path: 文件路径
    """
    try:
        return_code = os.system("start " + file_path)
        if return_code == 0:
            log.logger.info('已打开文件：' + file_path)    
        else:
            log.logger.error('打开文件失败！')
    except Exception as e:
        log.logger.error('打开文件失败！')
        log.logger.error(e)
>>>>>>> 6c0b95ef8a36d5d56bb1e47e255c35b967a128a8
        return