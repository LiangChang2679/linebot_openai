from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Global lists for participants
participants = {
    '狗狗': [],
    '逆轉': [],
}

# Function to handle addition of players
def add_players(category, names):
    if category not in participants:
        return "無效的類別"
    
    existing = participants[category]
    added_names = []
    for name in names:
        if name not in existing:
            existing.append((name, datetime.datetime.now()))  # Save name with timestamp
            added_names.append(name)
    
    participants[category] = sorted(existing, key=lambda x: x[1])  # Sort by timestamp
    
    if not added_names:
        return "所有玩家都已在名單中"
    else:
        return "已新增玩家: " + ", ".join(added_names)


# Function to handle removal of players
def remove_players(category, names):
    if category not in participants:
        return "無效的類別"
    
    existing = participants[category]
    removed_names = []
    for name in names:
        if name in existing:
            existing.remove(name)
            removed_names.append(name)
    
    if not removed_names:
        return "名單中沒有匹配的玩家"
    else:
        return "已移除玩家: " + ", ".join(removed_names)


# Function to handle listing of players
def list_players(category):
    if category not in participants:
        return "無效的類別"
    
    existing = participants[category]
    if not existing:
        return "名單是空的"
    else:
        return "\n".join([name for name, _ in existing])


# Function to handle drawing of players
def draw_players(category, num):
    if category not in participants:
        return "無效的類別"
    
    existing = participants[category]
    if num > len(existing):
        return "玩家數量不足以抽取"
    
    winners = random.sample(existing, num)
    return "獲獎者: " + ", ".join(winners)


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# Handler function
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    reply_text = '我不明白你的指令，請再試一次。'  # Default response

    if message.startswith('/add'):
        parts = message.split(' ')
        category = parts[1]
        names = parts[2].split(',')
        reply_text = add_players(category, names)
    elif message.startswith('/remove'):
        parts = message.split(' ')
        category = parts[1]
        names = parts[2].split(',')
        reply_text = remove_players(category, names)
    elif message.startswith('/list'):
        category = message.split(' ')[1]
        reply_text = list_players(category)
    elif message.startswith('/draw'):
        parts = message.split(' ')
        category = parts[1]
        num = int(parts[2])
        reply_text = draw_players(category, num)

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))
       
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
