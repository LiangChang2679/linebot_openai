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

participants = []
participants_reverse = []
winners = []

allowed_users = ['如如咪', '魚兒🦈' , 'Liang']

def add_participant(name, prize, position=None):
    global participants
    global participants_reverse

    if prize == '逆轉':
        names = name.split(',')  # 將名字以逗號分隔
        added_names = []
        for n in names:
            n = n.strip()
            if any(p[0] == n for p in participants):
                continue
            participants.append((n, datetime.now().date()))
            added_names.append(n)
        return added_names
    elif prize == '狗狗':
        if any(p[0] == name for p in participants_reverse):
            return []
        if position is None or position >= len(participants_reverse):
            participants_reverse.append((name, datetime.now().date()))
        else:
            participants_reverse.insert(position, (name, datetime.now().date()))
        return [name]

def remove_participant(name, prize):
    global participants
    global participants_reverse

    if name not in allowed_users:
        return

    if prize == '逆轉':
        if ',' in name:
            names = name.split(',')
            removed_names = []
            for n in names:
                participants = [p for p in participants if p[0] != n.strip()]
                removed_names.append(n.strip())
            reply_text = f'{", ".join(removed_names)} 已成功移出「逆轉」技能書的抽獎名單！'
        else:
            if (name, datetime.now().date()) not in participants:
                reply_text = f'{name} 不在「逆轉」技能書的抽獎名單內！'
            else:
                participants = [p for p in participants if p[0] != name.strip()]
                reply_text = f'{name} 已成功移出「逆轉」技能書的抽獎名單！'
    if prize == '狗狗':
        if ',' in name:
            names = name.split(',')
            removed_names = []
            for n in names:
                participants = [p for p in participants if p[0] != n.strip()]
                removed_names.append(n.strip())
            reply_text = f'{", ".join(removed_names)} 已成功移出「狗狗」的參加名單！'
        else:
            if (name, datetime.now().date()) not in participants:
                reply_text = f'{name} 不在「狗狗」的參加名單內！'
            else:
                participants = [p for p in participants if p[0] != name.strip()]
                reply_text = f'{name} 已成功移出「狗狗」的參加名單！'

def list_participants(prize):
    if prize == '逆轉':
        participant_list = ''
        sorted_participants = sorted(participants, key=lambda p: p[1])
        for i, participant in enumerate(sorted_participants, start=1):
            name, date = participant
            participant_list += f'{i}. {name} ({date.strftime("%m-%d")})\n'
        return participant_list
    elif prize == '狗狗':
        participant_list = ''
        for i, participant in enumerate(participants_reverse, start=1):
            name, date = participant
            participant_list += f'{i}. {name} ({date.strftime("%m-%d")})\n'
        return participant_list

def draw_winners(prize, num):
    global participants
    global winners

    if prize == '逆轉':
        participant_list = [participant[0] for participant in participants]
        if num > len(participant_list):
            return None

        if len(participants) == 0:
            reply_text = '目前沒有任何人參加抽獎。'
        else:
            random.shuffle(participant_list)
            winners = participant_list[:num]
            participants = [(participant, datetime.now().date()) for participant in participant_list[num:]]
            reply_text = f'恭喜以下人員獲得「逆轉」技能書：\n'
            for i, winner in enumerate(winners, start=1):
                reply_text += f'{i}. {winner}\n'

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


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    reply_text = '我不明白你的指令，請重試。'  # 預設的回覆訊息
        
    if message.startswith('/add 逆轉'):
        params = message.split('/add 逆轉 ')[1].split(',')
        added_names = []
        for name in params:
            added = add_participant(name.strip(), '逆轉')
            added_names.extend(added)
        if added_names:
            reply_text = f'{", ".join(added_names)} 已成功加入「逆轉」技能書的抽獎名單！'
        else:
            reply_text = '指定的玩家已經在名單中。'
        
    elif message.startswith('/add 狗狗'):
        params = message.split('/add 狗狗 ')[1].split(',')
        added_names = []
        for name in params:
            added = add_participant(name.strip(), '狗狗')
            added_names.extend(added)
        if added_names:
            reply_text = f'{", ".join(added_names)} 已成功加入「狗狗」的參加名單！'
        else:
            reply_text = '指定的玩家已經在名單中。'

        elif message.startswith('/remove 逆轉'):
            name = message.split('/remove 逆轉 ')[1]
            remove_participant(name, '逆轉')

        elif message.startswith('/remove 狗狗'):
            name = message.split('/remove 狗狗 ')[1]
            remove_participant(name, '狗狗')

        elif message == '/list 逆轉':
            participant_list = list_participants('逆轉')
            if participant_list:
                reply_text = '「逆轉」技能書的抽獎名單：\n' + participant_list
            else:
                reply_text = '目前沒有任何人參加「逆轉」技能書的抽獎。'

        elif message == '/list 狗狗':
            participant_list = list_participants('狗狗')
            if participant_list:
                reply_text = '「狗狗」的參加名單：\n' + participant_list
            else:
                reply_text = '目前沒有任何人參加「狗狗」。'

        elif message.startswith('/draw 逆轉'):
            num = int(message.split('/draw 逆轉 ')[1])
            reply_text = draw_winners('逆轉', num)

        elif message == '/小秘書':
            reply_text = '''【倚窗聽雨可愛小秘書指令說明】
        
            1. /add 逆轉 {名字1,名字2,...} - 將玩家加入「逆轉」技能書的抽獎名單，可一次新增多個玩家。
            2. /add 狗狗 {名字1,名字2,...} - 將玩家加入「狗狗」的參加名單，可一次新增多個玩家。
            3. /remove 逆轉 {名字} - 將玩家移出「逆轉」技能書的抽獎名單。
            4. /remove 狗狗 {名字} - 將玩家移出「狗狗」的參加名單。
            5. /list 逆轉 - 查看「逆轉」技能書的抽獎名單。
            6. /list 狗狗 - 查看「狗狗」的參加名單。
            7. /draw 逆轉 {數量} - 從「逆轉」技能書的抽獎名單中抽取指定數量的獲獎者。'''

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
