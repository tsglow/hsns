from newspaper import Article

url = 'http://www.digitaltoday.co.kr/news/articleView.html?idxno=262758'
a = Article(url, language='ko')

a.download()
a.parse()

print(a.text)


