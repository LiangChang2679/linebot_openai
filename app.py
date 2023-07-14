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
    '狗狗': [('卡帥', datetime.datetime.now())],
    '逆轉': [],
}

# Function to handle addition of players
def add_players(category, names):
    existing = participants.get(category, [])
    added_names = []
    for name in names:
        if name not in existing:
            existing.append((name, datetime.datetime.now()))  # Save name with timestamp
            added_names.append(name)
    
    participants[category] = sorted(existing, key=lambda x: x[1])  # Sort by timestamp
    
    if not added_names:
        return "呀嗨~你輸入的玩家都已經在「{}」名單裡啦！".format(category)
    else:
        return "耶！已經成功把玩家加到「{}」名單中了哦：{}".format(category, "、".join(added_names))


# Function to handle removal of players
def remove_players(category, names):
    existing = participants.get(category, [])
    removed_names = []
    for name in names:
        if name in existing:
            existing.remove(name)
            removed_names.append(name)
    
    if not removed_names:
        return "咦？你提供的玩家名字，我在「{}」的名單裡找不到呢！".format(category)
    else:
        return "哎呀！我已經從「{}」名單中移除這些玩家了：{}".format(category, "、".join(removed_names))


# Function to handle listing of players
def list_players(category):
    existing = participants.get(category, [])
    if not existing:
        return "哎呀！「{}」的名單裡現在空空如也呢。".format(category)
    else:
        return "「{}」名單裡的玩家有：\n{}".format(category, "\n".join([name for name, _ in existing]))


# Function to handle drawing of players
def draw_players(category, num):
    existing = participants.get(category, [])
    if num > len(existing):
        return "哎呀！「{}」的名單裡的玩家數量不夠我抽取呢。".format(category)
    
    winners = random.sample(existing, num)
    return "呼啦！以下這些玩家在「{}」中抽中「逆轉」技能書囉：{}".format(category, ", ".join(winners))


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
    reply_text = ''  # Default response

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
    elif message == '/小秘書':
        reply_text = '''【小秘書指令說明】
        
        1. /add {類別} {名字1,名字2,...} - 將玩家加入到指定類別的名單中，可以一次新增多個玩家。
        2. /remove {類別} {名字} - 從指定類別的名單中移除玩家，可以一次移除多個玩家。
        3. /list {類別} - 查看指定類別的名單。
        4. /draw {類別} {數量} - 從指定類別的名單中抽取指定數量的玩家。
        類別只有狗狗跟逆轉技能書

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))
       
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
