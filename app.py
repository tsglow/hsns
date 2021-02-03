import newspaper
import requests
import operator
import pandas as pd
import re
import datetime
from datetime import date
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from operator import itemgetter
from newspaper import Article



# 최종 결과 list. 전역으로 해야 할지 고민 중
scrapped_news = []
new_site_info = []
new_site_info_error = []



# 기본 설정
NA_id = "IHh_ePMGCQVkZkjIZ1CA"
NA_psd = "AzbXHQ6BTA"
now = datetime.datetime.now()
search_time = now.strftime('%Y-%m-%d')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'X-Naver-Client-Id': NA_id,
    'X-Naver-Client-Secret': NA_psd}


headers2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


#newspaper 모듈로 기사 본문 가져오기. ssl certificate에러 나면 스킵
def make_text (nlink):    
    try:
        a = Article(nlink, language='ko', headers=headers2, verify=False)
        a.download()
        a.parse()
    except :
        text = "본문을 가져올 수 없습니다(SSL Certificate 에러)"
        return text
    else:        
        text = a.text
        return text

# pubDate를 datetime type으로 변환
def convert_time(time):
    strip = datetime.datetime.strptime(time, '%a, %d %b %Y %H:%M:%S +0900')
    converted_str = strip.strftime('%Y-%m-%d %H:%M:%S')
    converted = datetime.datetime.strptime(converted_str, '%Y-%m-%d %H:%M:%S')
    return converted


#title 값을 제대로 받아오면 site_info에 아니면  info_error에 추가
def make_site_info(domain, brand):
    site_info = {                  
        "domain" : domain,
        "brand" : brand}
    if domain == brand :
        new_site_info_error.append(site_info)
    else :
        new_site_info.append(site_info)


# domain url로 신문사 title tag 가져오기
# 먼저 site_db 에 있는지 체크. 그 다음에 new_site_info에 있는지 체크. 그래도 없으면 make soup 후 make_site_info
def get_brand(domain, site_db):    
    if any(d['domain'] == domain for d in site_db):
        site_info = next(item for item in site_db if item['domain'] == domain)
        brand = site_info['brand']
        return brand
    elif any(d['domain'] == domain for d in new_site_info):
        site_info = next(item for item in new_site_info if item['domain'] == domain)
        brand = site_info['brand']
        return brand
    elif any(d['domain'] == domain for d in new_site_info_error):
        site_info = next(item for item in new_site_info_error if item['domain'] == domain)
        brand = site_info['brand']
        return brand    
    else:
        try:            
            rst = requests.get(f"http://{domain}", allow_redirects=True, timeout=10, headers=headers2, verify=False)
        except:
            brand = domain
            make_site_info(domain, brand)            
            return  brand
        else:
            print(f'now checking {domain}')
            rst.encoding = rst.apparent_encoding # 원문 기사 인코딩 방식대로 인코딩처리(euc-kr로 나타내는게 목적이지만 python이 인식한 것에 기반하므로 정확하지 않음)
            soup = BeautifulSoup(rst.text, 'html.parser')
            try:
                brand = soup.find("head").find("title").string
            except:                
                brand = domain
                make_site_info(domain, brand)
                return  brand
            else:
                make_site_info(domain, brand)
                return brand
            


# api로 받아온 기사 내용에서 검색어를 강조하는 <b> 태그와 공백 제거하는 함수
def remove_tag(news):
    x = str(news.get('title'))
    x = re.sub('<.+?>', '', x, 0, re.I | re.S)
    x = re.sub('&quot;', '', x, 0, re.I | re.S)
    y = str(news.get('description'))
    y = re.sub('<.+?>', '', y, 0, re.I | re.S)
    y = re.sub('&quot;', '', y, 0, re.I | re.S)
    news['title'] = str(x)
    news['description'] = str(y)




# 기사 내용을 사이트명, 기사제목, 본문내용, 시간, 검색키워드, link 로 세분화해 dict에 저장하는 함수
def make_article(news, nlink, cat, time, site_db):
    extract_domain = nlink.split('/')
    domain = extract_domain[2]
    brand = get_brand(domain, site_db)        
    remove_tag(news)
    text = make_text(nlink)    
    result = {
        'domain': brand,
        'title': news['title'],
        'description': news['description'],
        'pubDate': time,
        'cat': cat,
        'link': nlink,
        'text' : text
    }
    scrapped_news.append(result)



# 중복기사인 경우 cat 내용만 추가, 신규면 make article
def merge_or_make_article(news,key, time, site_db):
    nlink = news['originallink']
    cat = key
    if any(d['link'] == nlink for d in scrapped_news):
        search_overlap = next(item for item in scrapped_news if item['link'] == nlink)
        old_cat = search_overlap['cat']
        search_overlap['cat'] = f'{old_cat}, {cat}'
    else :
        make_article(news, nlink, cat, time, site_db)        



# 기사 시간 체크 후 merge or make article 로
def article_check(newslist, key, site_db):
    w_day = now.weekday()  # 요일체크
    for news in newslist:
        time = convert_time(news['pubDate'])
        tminus = (now - time).days
        if w_day == 0 and tminus <= 3:  # 월요일이면 3일치 기사 스크랩
            merge_or_make_article(news,key, time, site_db)
        elif w_day != 0 and tminus <= 1:  # 월요일 아니면 1일치 기사 스크랩
            merge_or_make_article(news,key, time, site_db)            
        else:
            pass



# 네이버 뉴스 api 에서 key 를 검색해 기사를 받아오는 함수
# home.html 에서 args로 넘겨준 값을 검색 키워드로 하여 API로 데이터 받아오기
# for avoind bot blocker : requests.get(url, headers=headers)
def get_news(key,site_db):
    search_word = key  # 검색어
    encode_type = 'json'  # 출력 방식 json 또는 xml
    max_display = 6  # 출력 뉴스 수
    sort = 'sim'  # 결과값의 정렬기준 시간순 date, 관련도 순 sim
    start = 1  # 출력 위치
    url = f'https://openapi.naver.com/v1/search/news.{encode_type}?query="{search_word}"&display={str(int(max_display))}&start={str(int(start))}&sort={sort}'
    r = requests.get(url, headers=headers)
    newslist = r.json()["items"]
    article_check(newslist, key, site_db)


#시동함수
def handle_keyword():
    news_cat = keyword_load()
    from_site_csv = pd.read_csv('site_title.csv') #site db로딩
    site_db = from_site_csv.to_dict('records')            
    for key in news_cat:            
        get_news(key,site_db)
    sorted_scrapped_news = sorted(scrapped_news, key=itemgetter('pubDate'), reverse=True)
    news_df = pd.DataFrame(sorted_scrapped_news)
    news_df.to_csv(f'news_at_{search_time}.csv', index=False)
    site_df = pd.DataFrame(new_site_info)
    site_df.to_csv('site_title.csv', mode='a', header=None, index=False)
    site_error_df = pd.DataFrame(new_site_info_error)
    site_error_df.to_csv('site_title.csv', mode='a', header=None, index=False)
    site_error_df.to_csv('site_title_error.csv', mode='a', header=None, index=False)


#검색어 db 에서 검색어 가져오는 함수
def keyword_load():     
    from_csv = pd.read_csv('keyword.csv')    
    news_cat = from_csv.search_word.to_list()
    return news_cat            


#kisa alert 가져오는 함수
def get_kisa_status():
    r = requests.get("https://www.krcert.or.kr/main.do")
    soup = BeautifulSoup(r.text, "html.parser")
    t_info = soup.find("div", {"class": "inWrap"}).find("span", {"class": "state"}).string  # kisa 인터넷 경보 정보
    return t_info


# Flask 앱 이름
app = Flask("Homeplus Securiy News Scrapper")


# Flask 기본 페이지. 검색할 키워드와  kisa 인터넷 경보 정보를 표시
@ app.route("/")
def scrap():
    scrapped_news.clear
    t_info = get_kisa_status()    
    try:
        from_news_db = pd.read_csv(f'news_at_{search_time}.csv') #news db로딩
        sorted_scrapped_news = from_news_db.to_dict('records')
        last_article = sorted_scrapped_news[0]
        dead_line = last_article['pubDate']        
        # if sorted_scrapped_news[0].pubdate < 1: 중복되지 않은 기사는 스크랩
    except:
        news_cat = keyword_load()
        from_site_csv = pd.read_csv('site_title.csv') #site db로딩
        site_db = from_site_csv.to_dict('records')            
        for key in news_cat:            
            get_news(key,site_db)
        sorted_scrapped_news = sorted(scrapped_news, key=itemgetter('pubDate'), reverse=True)
        news_df = pd.DataFrame(sorted_scrapped_news)
        news_df.to_csv(f'news_at_{search_time}.csv', index=False)
        site_df = pd.DataFrame(new_site_info)
        site_df.to_csv('site_title.csv', mode='a', header=None, index=False)
        site_error_df = pd.DataFrame(new_site_info_error)
        site_error_df.to_csv('site_title.csv', mode='a', header=None, index=False)
        site_error_df.to_csv('site_title_error.csv', mode='a', header=None, index=False)
    return render_template("home.html",  t_info=t_info, article=sorted_scrapped_news, count=len(sorted_scrapped_news), today=search_time)


# Flask 검색 설정 페이지.
@ app.route("/read")
def home():    
    return render_template("read.html")


# repl에서 돌릴때 마지막에 필요함
# #app.run(host="0.0.0.0")
