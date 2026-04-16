from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from  firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup


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
    homepage = "<h1>林憲墉Python網頁20260409</h1>"
    homepage += "<a href=/hank>hank</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=hank>傳送使用者暱稱</a><br>"
    homepage += "<a href=/account>網頁表單傳值</a><br>"
    homepage += "<a href=/about>憲墉簡介網頁</a><br>"
    homepage += "<a href=/add>次方與根號計算</a><br>"
    homepage += "<br><a href=/read>讀取Firestore資料</a><br>"
    homepage += "<br><a href=/read2>讀取Firestore資料(根據關鍵字:楊</a><br>"
    homepage += "<br><a href=/spider>爬蟲</a><br>"

    return homepage
@app.route("/read")
def read():
    Result = ""
    keyword  = "楊"
    db = firestore.client()
    collection_ref = db.collection("資管class")    
    docs = collection_ref.get()    
    for doc in docs:         
        teacher = doc.to_dict()
        keyword
        if keyword in teacher["name"]:
                print(teacher)
        if Result == "":
            Result = "抱歉查無此人"  
    return Result
@app.route("/read2")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("資管class")    
    docs = collection_ref.get()    
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result
	
@app.route("/hank")
def course():
    return "<h1>資訊管理導論</h1>"

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
@app.route("/spider")
def spider():
    Result = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")
    for i in result:
        result += i.test + i.get("herf") + "<br>"
        return Result

  

if __name__ == "__main__":
    app.run()
  