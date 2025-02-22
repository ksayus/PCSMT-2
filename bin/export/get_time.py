import datetime

today = datetime.date.today()
this_year = today.year
this_month = today.month
this_day = today.day

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