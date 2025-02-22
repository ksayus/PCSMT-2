import logging
import os
from bin.export import get_time
from bin.find_files import find_folder

now_work_path = os.getcwd()

logger = logging.getLogger('PCSMT_log')
logger.setLevel(logging.DEBUG)

work_path = os.getcwd()

find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year))
find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year) + '/' + str(get_time.this_month))
find_folder.find_folders_with_existence_and_create(work_path + '/logs/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day))

if find_folder.find_folders_with_existence("logs"):
    if find_folder.find_folders_with_existence(now_work_path + '/logs' + '/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day)):

        now_time = get_time.now_time()
        file_handler = logging.FileHandler(now_work_path + '/logs' + '/' + str(get_time.this_year) + '/' + str(get_time.this_month) + '/' + str(get_time.this_day) + '/' + now_time + ".log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    else:
        print("日志文件夹不存在")