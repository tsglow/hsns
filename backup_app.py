import requests
import operator
import pandas as pd
import re
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from datetime import date


# 검색어 카테고리
news_cat = [
    "랜섬",
    "솔라윈즈",
    "보안 취약점",
    "리눅스",
    "정보유출",
    "클라우드",
    "방화벽",
]

# 최종 결과 list. 전역으로 해야 할지 고민 중
scrapped_news = []

# 기본 설정
NA_id = "IHh_ePMGCQVkZkjIZ1CA"
NA_psd = "AzbXHQ6BTA"
date = date.today()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'X-Naver-Client-Id': NA_id,
    'X-Naver-Client-Secret': NA_psd}


headers2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


# 기사 중복체크 함수
def article_check(nlink):
    for dict in scrapped_news:  # list에서 dict값 소환
        for item in dict:
        print()


# html title tag 에서 신문사 이름 받아오는 함수. title tag 가 없을 경우 domain으로 처리함
def get_brand(domain):
    rst = requests.get(
        f"http://{domain}", allow_redirects=True, timeout=10, headers=headers2,)
    # 원문 기사 인코딩 방식대로 인코딩처리(euc-kr로 나타내는게 목적이지만 python이 인식한 것에 기반하므로 정확하지 않음)
    rst.encoding = rst.apparent_encoding
    soup = BeautifulSoup(rst.text, 'html.parser')
    try:
        brand = soup.find("head").find("title").string
        return brand
    except:
        brand = domain
        return brand


# api로 받아온 기사 내용에서 검색어를 강조하는 <b> 태그와 공백 제거하는 함수
def remove_tag(news):
    x = str(news.get('title'))
    x = re.sub('<.+?>', '', x, 0, re.I | re.S)
    x = re.sub('&quot;', '', x, 0, re.I | re.S)
    y = str(news.get('description'))
    y = re.sub('<.+?>', '', y, 0, re.I | re.S)
    news['title'] = str(x)
    news['description'] = str(y)


# 기사 내용을 사이트명, 기사제목, 본문내용, 시간, 검색키워드, link 로 세분화해 dict에 저장하는 함수
def make_article(newslist, key):
    for news in newslist:
        nlink = news['originallink']
        cat = key
        # link로 이미 같은 기사가 수집되었는지 확인
        if article_check:
            print("중복")
            pass
        else:
            extract_domain = link.split('/')
            domain = extract_domain[2]
            brand = get_brand(domain)
            remove_tag(news)
            result = {
                'domain': brand,
                'title': news['title'],
                'description': news['description'],
                'pubDate': news['pubDate'],
                'cat': key,
                'link': nlink
            }
            scrapped_news.append(result)


# 네이버 뉴스 api 에서 key 를 검색해 기사를 받아오는 함수
# home.html 에서 args로 넘겨준 값을 검색 키워드로 하여 API로 데이터 받아오기
# for avoind bot blocker : requests.get(url, headers=headers)
def get_news(key):
    search_word = key  # 검색어
    encode_type = 'json'  # 출력 방식 json 또는 xml
    max_display = 10  # 출력 뉴스 수
    sort = 'sim'  # 결과값의 정렬기준 시간순 date, 관련도 순 sim
    start = 1  # 출력 위치
    url = f'https://openapi.naver.com/v1/search/news.{encode_type}?query="{search_word}"&display={str(int(max_display))}&start={str(int(start))}&sort={sort}'
    r = requests.get(url, headers=headers)
    newslist = r.json()["items"]
    make_article(newslist, key)


# Flask 앱 이름
app = Flask("Homeplus Securiy News Scrapper")

# Flask 기본 페이지. 검색할 키워드와  kisa 인터넷 경보 정보를 표시


@ app.route("/")
def home():
    r = requests.get("https://www.krcert.or.kr/main.do")
    soup = BeautifulSoup(r.text, "html.parser")
    t_info = soup.find("div", {"class": "inWrap"}).find(
        "span", {"class": "state"}).string  # kisa 인터넷 경보 정보
    return render_template("home.html", news_cat=news_cat, t_info=t_info)


# Flask 검색 결과 페이지.
@ app.route("/read")
def scrap():
    keys_to_search = []    #
    selected = request.args  # check 한 단어들
    # new_cat의 키워드들 중에 check 한 단어 list에 있는 것만 keys_to_search list 로 넘기고, keys(후략) list의 원소마다 get_news함수로 뉴스를 받아옴
    for i in news_cat:
        if i in selected:
            keys_to_search.append(i)
    for key in keys_to_search:
        get_news(key)
    return render_template("read.html", article=scrapped_news)


# pandas로 데이터 프레임으로 변환 후 csv로 저장하기
# df = pd.DataFrame(r.json()['items'])
# df.to_csv(f'news_search_result_{search_word}.csv')

# repl에서 돌릴때 마지막에 필요함
# #app.run(host="0.0.0.0")
