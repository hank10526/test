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
            db.collection("電影2A").document(movie_id).set(doc)
            
        return f"爬蟲完成！最後更新日期：{lastUpdate}"
    except Exception as e:
        return f"爬蟲發生錯誤: {e}"

# ... 其餘 math, search, read 路由維持邏輯不變 ...

@app.route("/today")
def today():
    return render_template("today.html", datetime=str(datetime.now()))

if __name__ == "__main__":
    app.run(debug=True)
