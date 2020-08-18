from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import configparser
from google.cloud import storage

config = configparser.ConfigParser()
config.read('C:\\Users\\dream\\Desktop\\NKNU-LineBot\\config.ini')
access_token = config['LINE']['ACCESS_TOKEN']
secret = config['LINE']['SECRET']

app = Flask(__name__)
app.config['DEBUG'] = True

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text='HELLO!')
    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=ImageMessage)
def handle_ImageMessage(event):
    userSend = line_bot_api.get_message_content(event.message.id)
    with open('profile.jpg', 'wb') as fd:
        fd.write(userSend.content)
    message = TextSendMessage(text='Hi')
    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=FileMessage)
def handle_FileMessage(event):
    userSend = line_bot_api.get_message_content(event.message.id)
    # with open(event.message.file_name, 'wb') as fd:
    #     fd.write(userSend.content)
    # message = TextSendMessage(text=event.message.file_name)
    gcs = storage.Client.from_service_account_json('C:\\Users\\dream\\Desktop\\client_secrets.json')
    bucket = gcs.get_bucket('examplefornknuhp2020')
    blob = bucket.blob(event.message.file_name)
    blob.upload_from_string(data=userSend.content,content_type=userSend.content_type)
    message = TextSendMessage(text='{} is now at {}'.format(event.message.file_name,blob.public_url))
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
