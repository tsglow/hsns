import requests
import operator
import pandas as pd
import re
import datetime
from datetime import date
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from operator import itemgetter


# 검색어 카테고리
news_cat = [
    "랜섬",
    "솔라윈즈",
    "보안 취약점",
    "리눅스",
    "정보유출",
    "클라우드",
    "방화벽",
    "해커"
]

# 최종 결과 list. 전역으로 해야 할지 고민 중
scrapped_news = []

# 기본 설정
NA_id = "IHh_ePMGCQVkZkjIZ1CA"
NA_psd = "AzbXHQ6BTA"
now = datetime.datetime.now()
search_time = now.strftime('%Y-%m-%d')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
    'X-Naver-Client-Id': NA_id,
    'X-Naver-Client-Secret': NA_psd}


def scrap():
    scrapped_news.clear
    # 오늘 날짜로 작성된 db파일이 있나 검색
    from_db = pd.read_csv(f'news_at_{search_time}.csv')
    sorted_scrapped_news = from_db.to_dict(
        'records')  # 있다면 dict 로 이루어진 list로 불러옴
    print(sorted_scrapped_news)


scrap()
#    except:
#        for key in news_cat:
#            get_news(key)
#        sorted_scrapped_news = sorted(
#            scrapped_news, key=itemgetter('pubDate'), reverse=True)
#        df = pd.DataFrame(scrapped_news)
#        df.to_csv(f'news_at_{search_time}.csv')


# pandas로 데이터 프레임으로 변환 후 csv로 저장하기
# df = pd.DataFrame(r.json()['items'])
# df.to_csv(f'news_search_result_{search_word}.csv')

# repl에서 돌릴때 마지막에 필요함
# #app.run(host="0.0.0.0")
