import os
import json
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- Firebase 初始化邏輯 (修正重點) ---
def init_firebase():
    if not firebase_admin._apps:
        # 1. 優先嘗試讀取環境變數 (Vercel)
        firebase_config = os.getenv('FIREBASE_CONFIG')
        
        if firebase_config:
            try:
                cred_dict = json.loads(firebase_config)
                # 解決 Vercel 環境變數中 private_key 換行符號被轉義的問題
                if "private_key" in cred_dict:
                    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Firebase Config Error: {e}")
        # 2. 如果沒有環境變數，嘗試讀取本地檔案
        elif os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
        else:
            print("Warning: No Firebase credentials found.")

init_firebase()

# --- 路由 ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather", methods=["GET", "POST"])
def weather_query():
    result_text = ""
    if request.method == "POST":
        city = request.form.get("city", "").strip().replace("台", "臺")
        if city:
            # 氣象署 API
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName={city}"
            try:
                response = requests.get(url, timeout=10)
                data = response.json()
                if data.get("records") and data["records"].get("location"):
                    loc = data["records"]["location"][0]["weatherElement"]
                    weather = loc[0]["time"][0]["parameter"]["parameterName"]
                    rain = loc[1]["time"][0]["parameter"]["parameterName"]
                    result_text = f"{city} 目前天氣預報：<br>{weather}，降雨機率：{rain}%"
                else:
                    result_text = "找不到該縣市，請輸入完整名稱（如：臺中市）。"
            except Exception as e:
                result_text = f"API 連線失敗：{e}"
    return render_template("weather.html", result=result_text)

@app.route("/road")
def road():
    try:
        url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
        response = requests.get(url, timeout=10)
        data = response.json()
        res = [f"{i['路口名稱']}, 事故數: {i['總件數']}" for i in data]
        return "<br>".join(res)
    except Exception as e:
        return f"資料獲取失敗: {e}"

@app.route("/movie2")
def movie2():
    try:
        url = "http://www.atmovies.com.tw/movie/next/"
        data = requests.get(url)
        data.encoding = "utf-8"
        sp = BeautifulSoup(data.text, "html.parser")
        items = sp.select(".filmListAllX li")
        
        # 取得更新日期
        update_div = sp.find("div", class_="smaller09")
        lastUpdate = update_div.text[5:] if update_div else "Unknown"

        db = firestore.client()
        for item in items:
            title_div = item.find("div", class_="filmtitle")
            if not title_div: continue
            
            title = title_div.text
            link = title_div.find("a").get("href")
            movie_id = link.replace("/", "").replace("movie", "")
            
            runtime_text = item.find("div", class_="runtime").text.replace("上映日期：", "").replace("片長：", "").replace("分", "")
            
            doc = {
                "title": title,
                "picture": item.find("img").get("src").replace(" ", ""),
                "hyperlink": "http://www.atmovies.com.tw" + link,
                "showDate": runtime_text[0:10],
                "showLength": runtime_text[13:].strip(),
                "lastUpdate": lastUpdate
            }
            db.collection("靜宜資管").document(movie_id).set(doc)
            
        return f"爬蟲完成！最後更新日期：{lastUpdate}"
    except Exception as e:
        return f"爬蟲發生錯誤: {e}"

# ... 其餘 math, search, read 路由維持邏輯不變 ...
@app.route("/movie1")
def movie1():
    R = ""
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    for item in result:
        introduce = "https://www.atmovies.com.tw" + item.find("a").get("href")
        R +=  "<a href=" + introduce + ">" + item.find("img").get("alt") + "</a><br>"
        post = "https://www.atmovies.com.tw" + item.find("img").get("src")
        R += "<img src=" + post + "> </img><br><br>" 
    return R    

@app.route("/spider1")
def spider1():
    R = ""
    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box a")

    for i in result:
        R += i.text + i.get("href") + "<br>" 
    return R

@app.route("/search", methods=["GET", "POST"])
def search():
    db = firestore.client()
    results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword")
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()

        for doc in docs:
            user = doc.to_dict()
            if keyword in user["name"]:
                results.append({
                    "name": user["name"],
                    "lab": user["lab"]
                })

    return render_template("search.html", results=results, keyword=keyword)


@app.route("/read2")
def read2():
    Result = ""
    keyword = "楊"
    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.get()
    for doc in docs: 
        teacher = doc.to_dict()
        if keyword in teacher["name"]:        
            Result += str(teacher) + "<br>"

    if Result == "":
        Result = "抱歉,查無此關鍵字姓名之老師資料"    
    return Result

@app.route("/read")
def read():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026B")    
    docs = collection_ref.get()
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).get()
    for doc in docs:         
        Result += str(doc.to_dict()) + "<br>"    
    return Result

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime=str(now))

@app.route("/about")
def about():
    return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")    
    return render_template("welcome.html", name= user, dep = d, course = c)


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")


@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        x = int(request.form["x"])
        opt = request.form["opt"]
        y = int(request.form["y"])      
        result = "您輸入的是：" + str(x) + opt + str(y)
        
        if (opt == "/" and y == 0):
            result += "，除數不能為0"
        else:
            match opt:
                case "+":
                    r = x + y
                case "-":
                    r = x - y
                case "*":
                    r = x * y
                case "/":
                    r = x / y  # 修正：之前誤寫為 x - y
                case _:
                    return "未知運算符號"
            result += "=" + str(r)  + "<br><a href=/>返回首頁</a>"          
        return result
    else:
        return render_template("math.html")

@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)



@app.route("/math2", methods=["GET", "POST"])
def math2():
    result = None
    if request.method == "POST":
        # 取得使用者輸入
        x = int(request.form.get("x"))
        opt = request.form.get("opt")
        y = int(request.form.get("y"))

        # 你的核心邏輯
        match opt:
            case "∧":
                result = x ** y
            case "√":
                if y != 0:
                    result = x ** (1/y)
                else:
                    result = "數學上不存在「0 次方根」"
            case _:
                result = "請輸入∧(次方)或√(根號)"
    return render_template("math2.html", result=result)


@app.route("/today")
def today():
    return render_template("today.html", datetime=str(datetime.now()))

if __name__ == "__main__":
    app.run(debug=True)
