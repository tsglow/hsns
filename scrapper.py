import newspaper
import requests
import operator
import pandas as pd
import re
import datetime
from datetime import date
from pytz import timezone
from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect
from operator import itemgetter
from newspaper import Article
from load_write import append_todb, load_db_todict, load_db_tolist, write_todb

#----------app구조----------
# keywords.csv load -> 각 검색어를 naver news api 로 검색 -> 
# 일요일인 경우 3일, 그 외에는 1일분 검색 -> 중복 기사인 경우 검색어만 통합 -> 
# 뉴스 링크 도메인을 따와서 title.csv 에서 검색하고, 없으면 title tag를 bs4로 가져옴 -> 
# 기사 본문을 newspapper3k로 가져옴. 실패하면 그냥 navernews api description으로 대체 -> 
# 기사 제목, 사이트, 본문(description), 검색어로 news_at_{검색날짜}.csv로 저장 -> flask로 웹페이지로 뿌려줌
#---------------------------


#----------기본설정(전역변수)----------
#naver news api
NA_id = "IHh_ePMGCQVkZkjIZ1CA"
NA_psd = "AzbXHQ6BTA"
encode_type = 'json'  # 출력 방식 json 또는 xml
max_display = 6  # 검색어당 가져올 뉴스 수
sort = 'date'  # 결과값의 정렬기준 시간순 date, 관련도 순 sim
start = 1  # 출력 위치

#timestamp
#repl.it 에 올릴 때만 : current_timef = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
current_timef = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
current_time = datetime.datetime.strptime(current_timef, '%Y-%m-%d %H:%M:%S')
search_date = current_time.strftime('%Y-%m-%d')

#DB
keywords = load_db_tolist("keywords") 
media = load_db_todict("media")
new_media_info_error = []
new_media_info = []
news_list = []
scrapped_news = []
added_news = []


#naver news api header
headers_naver = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'X-Naver-Client-Id': NA_id,
    'X-Naver-Client-Secret': NA_psd}

#get_title_tag header
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

re_scrap_switch = "off"
#-----------------------------



def make_text(nlink):    
    try:
        a = Article(nlink, language='ko', headers=headers, verify=False)
        a.download()
        a.parse()
    except :        
        text = "본문을 가져올 수 없습니다(SSL Certificate 에러)"        
        return text
    else:                        
        text = a.text
        print(nlink, len(text))
        if len(text) < 40:
            text = "본문을 가져올 수 없습니다(newspaper3k가 내용을 가져오지 못함)"        
            return text
        else : 
            return text


def make_site_info(domain, name):
    site_info = {                  
        "domain" : domain,
        "media_name" : name}
    if domain == name :
        global new_media_info_error
        new_media_info_error.append(site_info)
    else :
        global new_media_info
        new_media_info.append(site_info)


def get_brand(domain):    
    if any(d['domain'] == domain for d in media):
        site_info = next(item for item in media if item['domain'] == domain)
        name = site_info['media_name']
        print("found it! in media")
        return name
    elif any(d['domain'] == domain for d in new_media_info):
        site_info = next(item for item in new_media_info if item['domain'] == domain)
        name = site_info['media_name']
        print("found it! in new_media")
        return name
    elif any(d['domain'] == domain for d in new_media_info_error):
        site_info = next(item for item in new_media_info_error if item['domain'] == domain)
        name = site_info['media_name']
        print("found it! in trash can")
        return name
    else:
        print(f'Can not find {domain} in db')
        try:            
            rst = requests.get(f"http://{domain}", allow_redirects=True, timeout=10, headers=headers, verify=False)
        except:
            name = domain
            make_site_info(domain, name)            
            return  name
        else:
            print(f'now checking {domain}')
            rst.encoding = rst.apparent_encoding # 원문 기사 인코딩 방식대로 인코딩처리(euc-kr로 나타내는게 목적이지만 python이 인식한 것에 기반하므로 정확하지 않음)
            soup = BeautifulSoup(rst.text, 'html.parser')
            try:
                name = soup.find("head").find("title").string
            except:                
                name = domain
                make_site_info(domain, name)
                return  name
            else:
                make_site_info(domain, name)
                return name
            


def remove_tag(news):
    x = str(news.get('title'))
    x = re.sub('<.+?>', '', x, 0, re.I | re.S)
    x = re.sub('&quot;', '', x, 0, re.I | re.S)
    y = str(news.get('description'))
    y = re.sub('<.+?>', '', y, 0, re.I | re.S)
    y = re.sub('&quot;', '', y, 0, re.I | re.S)
    news['title'] = str(x)
    news['description'] = str(y)


def make_article(news, nlink, cat, pubTime):
    extract_domain = nlink.split('/')
    domain = extract_domain[2]
    media_name = get_brand(domain)        
    remove_tag(news)
    text = make_text(nlink)
    result = {
        'media': media_name,
        'title': news['title'],
        'description': news['description'],
        'pubDate': pubTime,
        'cat': cat,
        'link': nlink,
        'text' : text
    }
    global scrapped_news, added_news
    if re_scrap_switch == "on":
        added_news.append(result)
    else:
        scrapped_news.append(result)


def merge_or_make_article(news,word,pubTime):
    nlink = news['originallink']
    cat = word
    if any(d['link'] == nlink for d in scrapped_news):
        search_overlap = next(item for item in scrapped_news if item['link'] == nlink)
        old_cat = search_overlap['cat']
        if cat in old_cat :
            pass
        else :
            search_overlap['cat'] = f'{old_cat}, {cat}'
    elif any(d['link'] == nlink for d in added_news):
        search_overlap = next(item for item in added_news if item['link'] == nlink)
        old_cat = search_overlap['cat']
        if cat in old_cat :
            pass
        else :
            search_overlap['cat'] = f'{old_cat}, {cat}'
    else :
        make_article(news,nlink,cat,pubTime)     

def convert_time(time):
    strip = datetime.datetime.strptime(time, '%a, %d %b %Y %H:%M:%S +0900')
    converted_str = strip.strftime('%Y-%m-%d %H:%M:%S')
    converted = datetime.datetime.strptime(converted_str, '%Y-%m-%d %H:%M:%S')
    return converted


def article_check(word, news_list):
    if re_scrap_switch == "on" :
        for news in news_list:
            pubTime = convert_time(news['pubDate'])
            if pubTime > dead_line : 
                merge_or_make_article(news,word,pubTime)
            else :
                pass
    else:
        w_day = current_time.weekday()  # 요일체크
        for news in news_list:
            pubTime = convert_time(news['pubDate'])
            dayDiff = (current_time - pubTime).days        
            if w_day == 0 and dayDiff < 3 :  # 월요일이면 72시간분 기사 스크랩                
                merge_or_make_article(news,word, pubTime)
            elif w_day != 0 and dayDiff <= 1:  # 월요일 아니면 48시간분 기사 스크랩            
                merge_or_make_article(news,word,pubTime)            
            else:            
                pass


def get_news(word):
    url = f'https://openapi.naver.com/v1/search/news.{encode_type}?query="{word}"&display={str(int(max_display))}&start={str(int(start))}&sort={sort}'
    news_request = requests.get(url, headers=headers_naver)
    news_list = news_request.json()["items"]
    article_check(word, news_list)

def get_current_time():
    current_timef = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_time = datetime.datetime.strptime(current_timef, '%Y-%m-%d %H:%M:%S')
    scrap_time_entry = {"time" : current_time}
    scrap_time = []
    scrap_time.append(scrap_time_entry)
    write_todb(scrap_time, "scrap_time")
    return current_time

def get_kisa_status():
    r = requests.get("https://www.krcert.or.kr/main.do")
    soup = BeautifulSoup(r.text, "html.parser")
    kisa_status = soup.find("div", {"class": "inWrap"}).find("span", {"class": "state"}).string
    return kisa_status


def scrap():
    try:
        global scrapped_news, current_time
        current_time = load_db_tolist("scrap_time")
        current_time = current_time[0]
        current_time = current_time['time']
        scrapped_news = load_db_todict(f'news_{search_date}')
        print("db loaded")
    except:
        current_time = get_current_time()        
        for word in keywords :
            get_news(word)
        sorted_scrapped_news = sorted(scrapped_news,key=itemgetter('pubDate'), reverse=True)
        write_todb(sorted_scrapped_news,f'news_{search_date}')        
        append_todb(new_media_info, 'media')
        append_todb(new_media_info_error, 'media_error')
        return sorted_scrapped_news
    else :
        return scrapped_news

def re_scrap():
    print("scrapping again")
    global scrapped_news, dead_line, re_scrap_switch, current_time
    current_time = get_current_time()
    scrapped_news = load_db_todict(f'news_{search_date}')
    last_news = scrapped_news[0]
    dead_line = last_news['pubDate']
    dead_line = datetime.datetime.strptime(dead_line, '%Y-%m-%d %H:%M:%S')
    re_scrap_switch = "on"
    for word in keywords :
        get_news(word)
    sorted_added_news = sorted(added_news,key=itemgetter('pubDate'), reverse=True)
    total_news = sorted_added_news + scrapped_news
    write_todb(total_news,f'news_{search_date}')
    write_todb(sorted_added_news,f'added_news_{current_time}')
    append_todb(new_media_info + new_media_info_error, 'media')
    append_todb(new_media_info_error, 'media_error')
    re_scrap_switch = "off"


