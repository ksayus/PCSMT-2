import os
from bin.export import log

class Open:
    def File(file_path):
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
            return