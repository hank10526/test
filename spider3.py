import requests

from bs4 import BeautifulSoup

url = "https://www.atmovies.com.tw/movie/next/"

Data = requests.get(url)
Data.encoding = "utf-8"

sp = BeautifulSoup(Data.text, "html.parser")

result=sp.find(id= "td iframe" )
for item in result:
    print(result.text)
