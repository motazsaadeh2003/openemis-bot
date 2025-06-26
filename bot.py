from flask import Flask, request
import requests

TOKEN = 'ضع_توكن_البوت_هنا'
CHAT_API = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

LOGIN_URL = 'https://emis.moe.gov.jo/openemis-core/users/login'
SEARCH_URL = 'https://emis.moe.gov.jo/openemis-core/Directory/Directories/Directories/index'

USERNAME = '9812042585'
PASSWORD = '9812042585'

app = Flask(__name__)

def login():
    session = requests.Session()
    payload = {
        "data[User][username]": USERNAME,
        "data[User][password]": PASSWORD
    }
    session.post(LOGIN_URL, data=payload)
    return session

def search_student(session, national_id):
    payload = {
        "AdvanceSearch[Directories][hasMany][identity_number]": national_id,
        "AdvanceSearch[Directories][isSearch]": "1"
    }
    r = session.post(SEARCH_URL, data=payload)
    return r.text

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        nat_id = data['message']['text'].strip()

        session = login()
        html = search_student(session, nat_id)

        if 'لم يتم العثور' in html:
            message = f'🚫 لا توجد بيانات للرقم الوطني: {nat_id}'
        else:
            message = f'✅ تم العثور على بيانات للرقم: {nat_id}\n(سيتم عرض التفاصيل لاحقًا)'

        requests.post(CHAT_API, data={'chat_id': chat_id, 'text': message})

    return 'ok'
