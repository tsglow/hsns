import datetime
from datetime import date


a = {"pubDate" : "2021-01-31 18:51:00"}
b = {"pubDate" : "2021-02-04 01:51:00"}

"""
def convert_time(time):
    strip = datetime.datetime.strptime(time, '%a, %d %b %Y %H:%M:%S +0900')
    converted = strip.strftime('%Y-%m-%d %H:%M:%S')
    return converted


def convert_to_strp(time):
    strip = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    converted_str = strip.strftime('%Y-%m-%d %H:%M:%S')
    converted = datetime.datetime.strptime(converted_str, '%Y-%m-%d %H:%M:%S')
    return converted


date = date.today()

if a["pubDate"] < b["pubDate"] :
    print("야옹")
else : 
    print("shit")

a = convert_to_strp(a["pubDate"])
b = convert_to_strp(b["pubDate"])


result = (b - a).seconds / 3600
print(result)

"""

time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
time_now = datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
search_time = time_now.strftime('%Y-%m-%d')

def convert_time(time):
    strip = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    converted_str = strip.strftime('%Y-%m-%d %H:%M:%S')
    converted = datetime.datetime.strptime(converted_str, '%Y-%m-%d %H:%M:%S')
    return converted

def article_check(a):
    w_day = time_now.weekday()  # 요일체크
    time = convert_time(a['pubDate'])
    tminus = (time_now - time).seconds
    if w_day == 0 and tminus <= 259200:  # 월요일이면 3일치 기사 스크랩
        print(tminus)        
    elif w_day != 0 and tminus <= 86400:  # 월요일 아니면 1일치 기사 스크랩
        print(tminus)        
    else:
        pass
print(time_now)
print(article_check(a))
print(article_check(b))