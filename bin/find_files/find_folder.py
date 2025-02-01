import os
from bin.export import log

def find_folders_with_existence_and_create(directory):
    if os.path.exists(directory):
        log.logger.info("文件夹存在:" + directory)
        return True
    else:
        log.logger.info("文件夹不存在，创建文件夹:" + directory)
        try:
            os.mkdir(directory)
            return True
        except OSError:
            log.logger.error("创建文件夹失败")
            return

def find_folders_with_existence(directory):
    if os.path.exists(directory):
        log.logger.info("文件夹存在:" + directory)
        return True
    else:
        log.logger.error("文件夹不存在:" + directory)
        return False