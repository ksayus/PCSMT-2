import datetime

today = datetime.date.today()
this_year = today.year
this_month = today.month
this_day = today.day

now = datetime.datetime.now()

def now_date_except_year():
    return today.strftime("%m/%d")

def now_date_except_year_and_month():
    return today.strftime("%d")

def now_time():
    return now.strftime("%H-%M-%S")

def now_time_except_hour():
    return now.strftime("%M-%S")

def now_time_except_hour_minute():
    return now.strftime("%S")