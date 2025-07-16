import datetime
import os
import json


work_path = os.getcwd()

class Time:
    Today = datetime.date.today()
    Year = Today.year
    Month = Today.month
    Day = Today.day
    Now = datetime.datetime.now()

    def __init__(self):
        self.Today = Time.Today
        self.Year = Time.Year
        self.Month = Time.Month
        self.Day = Time.Day
        self.Now = Time.Now

class TimeString:
    def DetailedTime():
        """
        返回当前日期
        示例:
        2020/01/01/00:00:00
        """
        return Time.Now.strftime("%Y/%m/%d/%H:%M:%S")
    def Month_Day():
        """
        返回当前日期，不包含年份
        示例:
        01/01
        """
        return Time.Now.strftime("%m/%d")

    def Day():
        """
        返回当前日期，不包含年份和月份
        示例:
        01
        """
        return Time.Now.strftime("%d")

    def Hour_Minute_Second():
        """
        返回当前时间，包含秒
        示例:
        01-01-01
        """
        return Time.Now.strftime("%H-%M-%S")

    def Minute_Second():
        """
        返回当前时间，不包含小时
        示例:
        01-01
        """
        return Time.Now.strftime("%M-%S")

    def Second():
        """
        返回当前时间，不包含小时和分钟
        示例:
        01
        """
        return Time.Now.strftime("%S")

    def Auto_Time():
        """
        返回当前时间，包含年份、月份、日期、小时
        示例:
        2021Y-01M-01D-01H
        """
        update_time = datetime.datetime.now()
        with open(work_path + '/config.json', 'r', encoding='utf-8') as f:
            config_read = json.load(f)
        StorageSizeUpdateTime = config_read['StorageSizeUpdateTime']

        if StorageSizeUpdateTime > 0 and StorageSizeUpdateTime < 60:
            return update_time.strftime('%Y年-%m月-%d日-%H时-%M分-%S秒')
        if StorageSizeUpdateTime > 60 and StorageSizeUpdateTime < 3600:
            return update_time.strftime('%Y年-%m月-%d日-%H时-%M分')
        if StorageSizeUpdateTime >= 3600 and  StorageSizeUpdateTime < 86400:
            return update_time.strftime("%Y年-%m月-%d日-%H时")
        if StorageSizeUpdateTime >= 86400 and  StorageSizeUpdateTime < 604800:
            return update_time.strftime("%Y年-%m月-%d日")
        if  StorageSizeUpdateTime >= 604800 and StorageSizeUpdateTime < 2592000:
            return update_time.strftime("%Y年-%m月")
        if StorageSizeUpdateTime >= 2592000 and StorageSizeUpdateTime < 31536000:
            return update_time.strftime("%Y年")