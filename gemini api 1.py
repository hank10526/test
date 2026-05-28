from google import genai

client = genai.Client(api_key='AIzaSyB-Tn_SmbOE48V8DhnD6sOImNd_vmMMHDE')

# 直接體驗最新一代的 3.5 Flash 
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents='今天天氣如何',
)

print(response.text)
