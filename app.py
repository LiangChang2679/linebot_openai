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
from datetime import datetime
import openai
import time
import random
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Global lists for participants
participants = {
    '狗狗': {'卡帥': datetime.now(), '帥卡': datetime.now(), '小喵魚': datetime.now(), '飄飄': datetime.now(), 'ano 花': datetime.now(), 'kura': datetime.now(),
           '姨媽': datetime.now(), '天山': datetime.now(), '拚打': datetime.now(), '阿傑': datetime.now()},
    '逆轉': {},
}

def add_players(category, names):
    if category not in ['狗狗', '逆轉']:
        return
    existing = participants.get(category, {})
    added_names = []
    for name in names:
        if name not in existing:
            existing[name] = datetime.datetime.now()
            added_names.append(name)
    
    participants[category] = existing
    if not added_names:
        return "呀嗨~你輸入的玩家都已經在「{}」名單裡啦！".format(category)
    else:
        return "耶！已經成功把玩家加到「{}」名單中了哦：{}".format(category, "、".join(added_names))

def remove_players(category, names):
    if category not in ['狗狗', '逆轉']:
        return
    existing = participants.get(category, {})
    removed_names = []
    for name in names:
        if name in existing:
            del existing[name]
            removed_names.append(name)
    
    if not removed_names:
        return "咦？你提供的玩家名字，我在「{}」的名單裡找不到呢！".format(category)
    else:
        return "哎呀！我已經從「{}」名單中移除這些玩家了：{}".format(category, "、".join(removed_names))

# Function to handle listing of players
def list_players(category):
    existing = participants.get(category, {})
    if not existing:
        return "哎呀！「{}」的名單裡現在空空如也呢。".format(category)
    else:
        player_list = []
        for name, timestamp in existing.items():
            player_list.append("{} - {}".format(name, timestamp.strftime("%m-%d %H:%M")))
        players = "\n".join(player_list)
        return "「{}」名單裡的玩家有：\n{}".format(category, players)

# Function to handle drawing of players
def draw_players(category, num):
    existing = participants.get(category)
    if not existing:
        return "哎呀！「{}」的名單裡現在空空如也呢。".format(category)

    participants_list = list(existing.keys())
    winners = random.sample(participants_list, num)
    return "呼啦！以下這些玩家在「{}」中抽中「逆轉」技能書囉：{}".format(category, ", ".join(winners))

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
    
def get_user_profile(user_id):
    profile = line_bot_api.get_profile(user_id)
    print("Display name:", profile.display_name)
    print("Picture URL:", profile.picture_url)
    print("Status message:", profile.status_message)
    print("User ID:", profile.user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    reply_text = ''  

    if message.startswith('/新增'):
        parts = message.split(' ')
        category = parts[1]
        names = parts[2].split(',')
        reply_text = add_players(category, names)
    elif message.startswith('/移除'):
        parts = message.split(' ')
        category = parts[1]
        names = parts[2].split(',')
        reply_text = remove_players(category, names)
    elif message.startswith('/清單'):
        category = message.split(' ')[1]
        reply_text = list_players(category)
    elif message.startswith('/抽獎'):
        parts = message.split(' ')
        category = parts[1]
        num = int(parts[2])
        reply_text = draw_players(category, num)
    elif message == '/小秘書':
        reply_text = '''【小秘書指令說明】
        
        1. /新增 {類別} {名字1,名字2,...} - 將玩家加入到指定類別的名單中，可以一次新增多個玩家。
        2. /移除 {類別} {名字} - 從指定類別的名單中移除玩家，可以一次移除多個玩家。
        3. /清單 {類別} - 查看指定類別的名單。
        4. /抽獎 {類別} {數量} - 從指定類別的名單中抽取指定數量的玩家。
        類別只有「狗狗」跟「逆轉」技能書'''

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))
       
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
