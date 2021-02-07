from newspaper import Article
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

url = 'https://www.chosun.com/international/international_general/2021/02/07/53R2NGMDQNBOPH6RB6LJEJ7ZL4/'
a = Article(url, headers=headers)

a.download()
a.parse()

print(type(a.text))
print(a.text)


