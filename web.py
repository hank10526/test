import requests
from bs4 import BeautifulSoup

from flask import Flask, render_template, request
from datetime import datetime

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)



app = Flask(__name__)

@app.route("/")
def index():
    # 使用原始字串或三引號讓 HTML 更整潔
    link = "<h1>憲墉Python網頁20260409</h1>"
    link += "<a href='/mis'>課程</a><hr>"
    link += "<a href='/today'>現在日期時間</a><hr>"
    link += "<a href='/welcome?u=子青&d=靜宜資管&c=資訊管理導論'>Get傳值</a><hr>"
    link += "<a href='/account'>POST傳值</a><hr>"
    link += "<a href='/read'>讀取Firestore資料(根據姓名關鍵字:楊)</a><hr>"
    link += "<a href='/read2'>讀取Firestore資料(全部)</a><hr>"
    link += "<a href='/spider1'>爬取子青老師課程資料</a><hr>"
    link += "<a href='/searchQ'>爬取即將上映電影到資料庫及關鍵字查詢</a><hr>"
    

    return link

@app.route("/mis") # 修正：補上路由註冊
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/read")
def read():
    result_str = "" # 建議變數小寫開頭以符合規範
    keyword = "楊"
    db = firestore.client()
    collection_ref = db.collection("資管class")    
    docs = collection_ref.get()    
    
    for doc in docs:        
        teacher = doc.to_dict()
        if keyword in teacher.get("name", ""): # 使用 .get 防止 Key不存在錯誤
            result_str += f"老師姓名：{teacher['name']} - 資料：{teacher}<br>"
    
    if result_str == "":
        return "抱歉查無此人"  
    return result_str

@app.route("/read2") # 修正：函式名稱改為 read2
def read2():
    result_str = ""
    db = firestore.client()
    collection_ref = db.collection("資管class")    
    docs = collection_ref.get()    
    for doc in docs:        
        result_str += "文件內容：{}<br>".format(doc.to_dict())   
    return result_str

@app.route("/movie1")
def movie1():
    r = ""
    url = "https://www.atmovies.com.tw/movie/next/"
    try:
        data = requests.get(url)
        data.encoding = "utf-8"
        sp = BeautifulSoup(data.text, "html.parser")
        result = sp.select(".filmListAllX li")
        for item in result:
            img_tag = item.find("img")
            a_tag = item.find("a")
            if img_tag and a_tag:
                r += f"電影名稱：{img_tag.get('alt')}<br>"
                r += f"介紹連結：https://www.atmovies.com.tw{a_tag.get('href')}<br>"
                r += f"<img src='{img_tag.get('src')}' width='100'><br><br>" # 這裡直接秀圖會比較酷
    except Exception as e:
        return f"爬蟲發生錯誤：{str(e)}"
    return r
@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))
@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)
@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")
@app.route("/searchQ", methods=["POST","GET"])

def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]:
                info += "片名：" + doc.to_dict()["title"] + "<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>"
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"
                return info

    else:

        return render_template("input.html")

# ... (其餘 today, welcome, account 保持不變) ...

if __name__ == "__main__":
    app.run(debug=True)