from flask import Flask, request
import requests
import os

app = Flask(__name__)

# جلب بيانات الدخول والتوكن من متغيرات البيئة
TOKEN = os.environ.get("TOKEN")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

LOGIN_URL = 'https://emis.moe.gov.jo/openemis-core/users/login'
SEARCH_URL = 'https://emis.moe.gov.jo/openemis-core/Directory/Directories/Directories/index'
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# دالة تسجيل الدخول إلى OpenEMIS
def login():
    session = requests.Session()
    payload = {
        "data[User][username]": USERNAME,
        "data[User][password]": PASSWORD
    }
    session.post(LOGIN_URL, data=payload)
    return session

# دالة البحث عن طالب باستخدام الرقم الوطني
def search_student(session, national_id):
    payload = {
        "AdvanceSearch[Directories][hasMany][identity_number]": national_id,
        "AdvanceSearch[Directories][isSearch]": "1"
    }
    response = session.post(SEARCH_URL, data=payload)
    return response.text

# نقطة استقبال الرسائل من Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        national_id = data["message"]["text"].strip()

        session = login()
        html = search_student(session, national_id)

        if "لم يتم العثور" in html:
            message = f"🚫 الرقم الوطني {national_id} غير موجود."
        else:
            message = f"✅ تم العثور على بيانات للرقم الوطني: {national_id}\n(عرض التفاصيل لاحقًا بإذن الله)"

        requests.post(TELEGRAM_API, data={"chat_id": chat_id, "text": message})
    return "ok"

# تشغيل السيرفر على Railway
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
