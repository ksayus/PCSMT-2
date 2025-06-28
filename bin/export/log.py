import logging
import os
from bin.export import get_time
from bin.find_files import find_folder
from bin.export import Is_program_running

now_work_path = os.getcwd()

logger = logging.getLogger('PCSMT_log')
logger.setLevel(logging.DEBUG)

work_path = os.getcwd()

find_folder.find_folders_with_existence_and_create(work_path + '/logs')
find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year))
find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year) + '/' + str(get_time.this_month))
find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day))

now_time = get_time.now_time()

# ANSI 颜色代码
COLORS = {
    'DEBUG': '\033[92m',    # 绿色
    'INFO': '\033[36m',     # 青色
    'WARNING': '\033[93m',  # 黄色
    'ERROR': '\033[91m',    # 红色
    'CRITICAL': '\033[95m', # 紫色
    'RESET': '\033[0m'      # 重置颜色
}

class ColorFormatter(logging.Formatter):
    """为不同日志级别添加颜色的自定义格式化器"""
    def format(self, record):
        # 获取原始日志消息
        message = super().format(record)
        # 根据日志级别添加颜色
        color = COLORS.get(record.levelname, COLORS['RESET'])
        return f"{color}{message}{COLORS['RESET']}"

if find_folder.find_folders_with_existence("logs"):
    if find_folder.find_folders_with_existence(now_work_path + '/logs' + '/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day)):

        file_handler = logging.FileHandler(now_work_path + '/logs' + '/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day) + '/' + now_time + ".log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    else:
        print("日志文件夹不存在")

def Debug(message: str):
    if Is_program_running.IsProgramExe():
        pass
    else:
        logger.debug(message)