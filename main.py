# -*- coding: utf-8 -*-
import os                       # ポート指定のため
import re                       # 正規表現
import gspread                  # GoogleSpreadSheetをいじるライブラリ
import httplib2
from flask import Flask, request,abort, jsonify    # Flask, JSON用  
from flask_cors import CORS     # CORS対策クロスオーバーリソースシェアリング
from oauth2client.service_account import ServiceAccountCredentials
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
CORS(app) # <-追加

####################################################################
#   GoogleSpreadSheet
####################################################################
SP_CREDNTIAL_FILE = 'client_secret2.json'
SP_SCOPE = 'https://spreadsheets.google.com/feeds'
SP_SHEET_KEY = '18JkP-HfYcoY4AO7e3eMkgApj1YSZW5Esv-yBflWyBZM'
SP_SHEET = '4月家計簿'

dict = {"食費" : "E5", "交通" : "E11", "お小遣い": "E7", "電気ガス" : "E6", "水道": "E12", "楽天": "E14"}
category = ''
####################################################################
#   LINEBOT 
####################################################################
line_bot_api = LineBotApi('R2vbh31gaxRKyyxQUG1/p6EsU0q+62QSwzVWM1oJR6MlKhnz3hCjSqCrb/ujvB9wEnd7zwinxx7IPjLX99g5X96LlLTWW9mPnEtrkhvqD/tErljr0Q+eWIiWZLNfpnZyZyLJ6oAMJN7+w5DJnj4tigdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('31aa9cd757b40ca322a14be96846a13a')

# test method
@app.route('/')
def hello():
    name = "Hello World"
    return name

# Python <--> Google Sheet APIテスト用
@app.route('/sheet')
def sheet():
    # スプレッドシートへの挿入準備（認証）----------
    sheet = get_authorize_sheet() # 下記参照
    # -------------------------------------------

    # val = sheet.acell(dict["食費"]).value
    # print(val)
    # print(dict)
    # print(dict["食費"])
    # records = sheet.get_all_records()

    # for r in records:
    #     print(r)

    return 'this api is /google sheet api!' # flaskでは何か返さないとエラーになるようだ

# LINE BOTで指定するメソッド
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# LINE BOTのメッセージを処理するメソッド
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # スプレッドシートへの挿入準備（認証）----------
    sheet = get_authorize_sheet() # 下記参照
    # -------------------------------------------
    text = event.message.text
    if re.search(r'[0-9]', text):
        chars = text.split(" ")
        print(chars[0])

        val = sheet.acell(dict[chars[0]]).value[1:] # 累計金額取得
        wk_money = chars[1] # 足そうとする金額
        money = int(val.replace(',','')) + int(wk_money) # 金額を足しこむ

        sheet.update_acell(dict[chars[0]], money) # 金額を更新する        
        text = "累計金額 : " + str(money)

    elif text.find("使い方") > -1:
        text = 'ex) 食費 1000 のように送信してねー\n使えるカテゴリ : \n{}\n{}\n{}\n{}\n{}'.format('食費','交通','お小遣い','電気ガス','水道')

    else:
        val = sheet.acell(dict[text.split(" ")[0]]).value
        text = text.split(" ")[0] + "は現在 " + val

    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=text))

# GoogleSpreadSheetを認証して、指定したシートを返すメソッド
def get_authorize_sheet():
    scope = [SP_SCOPE]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SP_CREDNTIAL_FILE, scope)
    client = gspread.authorize(credentials)
    sp = client.open_by_key(SP_SHEET_KEY)   # キーを使って、"Chiritsumo!2を開く"
    sheet = sp.worksheet(SP_SHEET)          # の中のシートを開く

    return sheet

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port)