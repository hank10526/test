from google import genai

client = genai.Client(api_key='AIzaSyB-Tn_SmbOE48V8DhnD6sOImNd_vmMMHDE')

question  = input("請輸入要問ai的問題")

# 直接體驗最新一代的 3.5 Flash 
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents = question,
)

print(response.text)
