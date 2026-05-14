import requests

from bs4 import BeautifulSoup

url = "http://www.atmovies.com.tw/movie/next/"

Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")

result=sp.find("img")

for item in result:
    print(item.text)
    print()


