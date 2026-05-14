import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

keyword = input("請輸入關鍵字(姓名")
collection_ref = db.collection("靜宜資管")
#docs = collection_ref.where(filter=FieldFilter("mail","==", "b0966031908@gmail.com")).get()
#docs = collection_ref.where(filter=FieldFilter("lab",">", "123")).get()
#docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(10).get()
#for doc in docs:
    #print(doc.to_dict())
docs = collection_ref.get()
for doc in docs:
        teacher = doc.to_dict()
        if keyword in teacher ["name"]:
            print(teacher)