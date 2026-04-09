from flask import Flask, render_template, request
from datetime import datetime
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

    return homepage
@app.route("/read")
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

  

if __name__ == "__main__":
    app.run()
  