# -*- coding: utf-8 -*-
import os                       # ポート指定のため
import re                       # 正規表現
from flask_cors import CORS     # CORS対策クロスオーバーリソースシェアリング
from flask import Flask, request,abort, jsonify    # Flask, JSON用  
app = Flask(__name__)
CORS(app) # <-追加

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

line_bot_api = LineBotApi('R2vbh31gaxRKyyxQUG1/p6EsU0q+62QSwzVWM1oJR6MlKhnz3hCjSqCrb/ujvB9wEnd7zwinxx7IPjLX99g5X96LlLTWW9mPnEtrkhvqD/tErljr0Q+eWIiWZLNfpnZyZyLJ6oAMJN7+w5DJnj4tigdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('31aa9cd757b40ca322a14be96846a13a')

@app.route('/')
def hello():
    name = "Hello World"
    return name

@app.route('/afternoon')
def afternoon():
    return "good afternoon!"

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #食費、ファッション、交際費なら○○円ですか？と聞く
    text = event.message.text
    print(text)
    if  text.find("食費") > -1:                           
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="何円ですか？"))

    elif text.find("ファッション") > -1:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="何円ですか？"))

    elif text.find("交際費") > -1:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="何円ですか？"))

    elif re.search(r'[0-9]', text):
        print("数字含む")

    else :
        category = text.split(" ")
        print(category)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port)