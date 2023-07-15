from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import tempfile, os
from datetime import datetime
import random
import sqlite3

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

# Database setup
db_path = os.path.join(os.path.dirname(__file__), 'participants.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Create participants and teachings tables if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS participants
                  (category TEXT, name TEXT, timestamp TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS teachings
                  (question TEXT, answer TEXT)''')

conn.commit()

# Existing code of add_players and remove_players functions...

def teach(question, answer):
    cursor.execute("INSERT INTO teachings VALUES (?, ?)", (question, answer))
    conn.commit()
    return "" 

def answer_question(question):
    cursor.execute("SELECT answer FROM teachings WHERE question=?", (question,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return ""

# Function to handle listing of players
def list_players(category):
    existing = get_participants(category)
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
    existing = get_participants(category)
    if not existing:
        return "哎呀！「{}」的名單裡現在空空如也呢。".format(category)

    participants_list = list(existing.keys())
    winners = random.sample(participants_list, num)
    # 清空名单
    save_participants(category, {})
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
        parts = message.split(' ')
        if len(parts) > 1 and parts[1] in ['狗狗', '逆轉']:
            category = parts[1]
            reply_text = list_players(category)
    elif message.startswith('/抽獎'):
        parts = message.split(' ')
        category = parts[1]
        num = int(parts[2])
        reply_text = draw_players(category, num)
    elif message.startswith('/教育'):
        parts = message.split(' ', 2)
        if len(parts) == 3: # Ensure correct formatting
            question = parts[1]
            answer = parts[2]
            reply_text = teach(question, answer)
        else:
            reply_text = "教育指令格式錯誤，請使用 '/教育 問題 答案' 的格式。"
    else:
        temp_reply = answer_question(message)
        if temp_reply:
            reply_text = temp_reply
    elif message == '/小秘書':
        reply_text = '''【小秘書指令說明】
        
        1. /新增 {類別} {名字1,名字2,...} - 將玩家加入到指定類別的名單中，可以一次新增多個玩家。
        2. /移除 {類別} {名字} - 從指定類別的名單中移除玩家，可以一次移除多個玩家。
        3. /清單 {類別} - 查看指定類別的名單。
        4. /抽獎 {類別} {數量} - 從指定類別的名單中抽取指定數量的玩家。
        5. /教育 {問題} {答案} - 教育小秘書回答特定問題的答案。
        類別只有「狗狗」跟「逆轉」技能書'''

    if reply_text:  # Only reply when there is a message
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
       
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
