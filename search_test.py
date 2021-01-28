"""
scrapped_news = []
"""

scrapped_news = [
    {'domain': "www.naver.com", 'title': "네이버", 'description': "오늘기사",
        'pubDate': "2020-10-20", 'cat': "랜섬", 'link': "1"},
    {'domain': "www.naver.com", 'title': "네이버", 'description': "오늘기사",
        'pubDate': "2020-10-20", 'cat': "랜섬", 'link': "2"},
    {'domain': "www.naver.com", 'title': "네이버", 'description': "오늘기사",
        'pubDate': "2020-10-20", 'cat': "랜섬", 'link': "3"},
    {'domain': "www.naver.com", 'title': "네이버", 'description': "오늘기사",
        'pubDate': "2020-10-20", 'cat': "랜섬", 'link': "4"}
]


link = "4"
cat = "숫자"


def check():
    if len(scrapped_news) == 0:
        a = {"domain": "www.naver.com",
             "title": "네이버", "cat": cat, "link": link}
        scrapped_news.append(a)
    else:
        if not any(d['link'] == link for d in scrapped_news):
            a = {"domain": "www.naver.com",
                 "title": "네이버", "cat": cat, "link": link}
            scrapped_news.append(a)
        else:
            pass


print(len(scrapped_news))
check()
print(scrapped_news)
