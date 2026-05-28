from flask import Flask
from google import genai

app = Flask(__name__)

# 在全域（函式外面）建立 Client 物件，只初始化一次即可，不用每次初始化
api_key = '你的金鑰貼這邊'
client = genai.Client(api_key='AIzaSyB-Tn_SmbOE48V8DhnD6sOImNd_vmMMHDE')

@app.route("/AI")
def AI():
    # 每次使用者拜訪該路徑時，直接使用全域的 client 呼叫模型
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents='我想查詢靜宜大學資管系的評價？',
    )
    
    # 回傳生成的文字
    return response.text
