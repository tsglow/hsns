import datetime
from datetime import date


aa = {"pubDate" : "2021-01-31 18:51:00"}
bb = {"pubDate" : "2021-02-04 01:51:00"}

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
    tminus_days = (time_now - time).days
    tminus_hours = (time_now - time).seconds / 3600
    print(tminus_days, tminus_hours) 
    if w_day == 0 and tminus_days <= 2:  # 월요일이면 3일치 기사 스크랩
        print("야옹")        
    elif w_day != 0 and tminus_days <= 1:  # 월요일 아니면 1일치 기사 스크랩
        print("멍멍")        
    else:
        print("깨갱")        

article_check(aa)
article_check(bb)


"""
분기방안 1
db를 불러온 후 다시 최신 pubdate를 불러와서 nowtime이랑 한시간 이내면 make article하고 다시 중복체크해서 추가

분기방안2
페이지에 db재작성 버튼을 설치. 누르면
db에서 불러오는 걸 list 1로 
신규 작성되는 article 은 list 2로 
article check시에 list1 의 pubdate를 인자로 넘겨주고, 이것보다 >한것만 추가  

"""