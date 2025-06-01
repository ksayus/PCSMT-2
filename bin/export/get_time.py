import datetime
import os
import json

today = datetime.date.today()
this_year = today.year
this_month = today.month
this_day = today.day

work_path = os.getcwd()

now = datetime.datetime.now()

def now_date_except_year():
    """
    返回当前日期，不包含年份
    示例:
    01/01
    """
    return today.strftime("%m/%d")

def now_date_except_year_and_month():
    """
    返回当前日期，不包含年份和月份
    示例:
    01
    """
    return today.strftime("%d")

def now_time():
    """
    返回当前时间，包含秒
    示例:
    01-01-01
    """
    return now.strftime("%H-%M-%S")

def now_time_except_hour():
    """
    返回当前时间，不包含小时
    示例:
    01-01
    """
    return now.strftime("%M-%S")

def now_time_except_hour_minute():
    """
    返回当前时间，不包含小时和分钟
    示例:
    01
    """
    return now.strftime("%S")

def now_time_year_month_day_hour():
    """
    返回当前时间，包含年份、月份、日期、小时
    示例:
    2021Y - 01M - 01D - 01H
    """
    update_time = datetime.datetime.now()
    with open(work_path + '/config.json', 'r', encoding='utf-8') as f:
        config_read = json.load(f)
    StorageSizeUpdateTime = config_read['Storage_Size_Update_Time']

    if StorageSizeUpdateTime > 0 and StorageSizeUpdateTime < 60:
        return update_time.strftime('%Y年 - %m月 - %d日 - %H时 - %M分 - %S秒')
    if StorageSizeUpdateTime > 60 and StorageSizeUpdateTime < 3600:
        return update_time.strftime('%Y年 - %m月 - %d日 - %H时 - %M分')
    if StorageSizeUpdateTime >= 3600 and  StorageSizeUpdateTime < 86400:
        return update_time.strftime("%Y年 - %m月 - %d日 - %H时")
    if StorageSizeUpdateTime >= 86400 and  StorageSizeUpdateTime < 604800:
        return update_time.strftime("%Y年 - %m月 - %d日")
    if  StorageSizeUpdateTime >= 604800 and StorageSizeUpdateTime < 2592000:
        return update_time.strftime("%Y年 - %m月")
    if StorageSizeUpdateTime >= 2592000 and StorageSizeUpdateTime < 31536000:
        return update_time.strftime("%Y年")