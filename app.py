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
    '狗狗': {},
    '逆轉': {}
}

custom_replies = {
    "烤墨魚": "三更半夜不要吃這麼好!",
    "烤玉米": "夯軟絲仔熊賀呷!",
    "砍墨魚": "兜兜兜兜兜兜兜兜",
    "炸花枝": "有想過墨魚的心情嗎?",
    "80墨魚": "墨魚:被80是我的興趣",
    "虐": "墨魚:突然有興致想被虐 我是躺的那位",
    "墨魚腳": "墨魚:沒關係 腳可以打斷10次",
    "渣墨魚": "墨魚:(挖鼻)",
    "墨魚麵": "中午來碗墨魚麵",
    "墨魚壽司": "墨魚壽司..(口水)",
    "墨魚餅": "如果是墨魚餅 我推薦栗米墨魚餅ㄛ~~",
    "墨魚需要拍拍": "尼最香尼最棒尼最惹人愛~~宵夜大家為你排一排",
    "鴨子": "怎麼蒸鴨子~~ 你拉著我說你有些魷魚~~",
    "欺負墨魚": "那你大家對你熱烈的愛意",
    "墨魚很聰明": "???",
    "炸墨魚": "所以我說那個醬汁呢?",
    "霸主": "墨魚中的霸主?   還是墨魚",
    "夢想" : "做人如果沒有夢想 那跟鹹墨魚有什麼分別",
    "爭" : "爭什麼 摻在一起做墨魚丸啊 笨蛋!",
    "年輕" : "這是史上最年輕的特級墨魚，御楓墨魚！",
    "玩墨魚" : "^_____^",
    "狼" : "您是要登記狗狗嗎~~請找花雪雪唷!",
    "不要玩小秘書" : "你真的很糟糕耶(ㆆᴗㆆ",
    "餓了" : "今晚我想來點烤墨魚0.0",
    "注意" : "注意! 注意還動阿",
    "輕鬆" : "咱們外表嚴肅 內心輕鬆，不要外表輕鬆 內心墨魚鬆",
    "墨魚義大利麵": "義大利麵：近豬者赤 近墨魚者黑",
    "墨魚滑蛋": "滑嫩墨魚遇上蛋，一言不合滑鍋外",
    "發威": "墨魚不發威 你當我花枝",
    "墨魚三明治": "夜路走多了 總匯墨魚三明治",
    "兜兜兜兜": "(花枝遭斬)",
    "游泳": "墨魚手中箭，游泳不穿衣",
    "旅行": "就算有旅行，少了你一切兜兜兜兜鹹墨魚＂,
    "努力": "努力不一定成功，但不努力一定輕鬆",
    "墨魚燉飯": "墨魚請大家吃墨魚燉飯^O^"
}

questions = [
    {'Q': '墨魚屬於什麼種類的生物呀？', 'A': '頭足綱'},
    {'Q': '墨魚使用什麼部位來保持浮力呢？', 'A': '氣室'},
    {'Q': '墨魚是冷血還是熱血動物呢？', 'A': '冷血'},
    {'Q': '墨魚可以變色嗎？', 'A': '可以'},
    {'Q': '墨魚的視力好不好呢？', 'A': '好'},
    {'Q': '墨魚的壽命通常有多長呢？', 'A': '2年'},
    {'Q': '墨魚有幾只腳呢？', 'A': '10'},
    {'Q': '墨魚有骨頭嗎？', 'A': '沒有'},
    {'Q': '墨魚是夜行性還是日行性的動物呢？', 'A': '夜行性'},
    {'Q': '墨魚是肉食還是草食的動物呢？', 'A': '肉食'},
    {'Q': '墨魚的呼吸器官是什麼呢？', 'A': '鰓'},
    {'Q': '墨魚的繁殖方式是胎生還是卵生的呢？', 'A': '卵生'},
    {'Q': '墨魚可以後退游泳嗎？', 'A': '可以'},
    {'Q': '墨魚釋放墨汁的主要目的是什麼？', 'A': '逃避天敵'},
    {'Q': '墨魚的眼睛有什麼獨特之處？', 'A': 'W形'},
    {'Q': '墨魚的色彩變化是通過什麼機構實現的？', 'A': '色素細胞'},
    {'Q': '墨魚通常在哪個季節繁殖？', 'A': '春季'},
    {'Q': '墨魚的主要食物是什麼？', 'A': '小魚和甲殼類動物'},
    {'Q': '墨魚在自然界中的天敵主要有哪些？', 'A': '鯊魚和鯨類'},
    {'Q': '墨魚的心臟有幾個室？', 'A': '三個'},
    {'Q': '墨魚的活動時間主要是什麼時候？', 'A': '夜晚'},
    {'Q': '墨魚在水中移動主要依靠什麼？', 'A': '噴射推進'},
    {'Q': '墨魚的身體是透明的嗎？', 'A': '不是'},
    {'Q': '墨魚能夠偽裝自己嗎？', 'A': '可以'},
    {'Q': '墨魚有幾個心臟？', 'A': '三個'},
    {'Q': '墨魚使用什麼方式來吸引配偶？', 'A': '顯示鮮艷的顏色'},
    {'Q': '墨魚在進食時主要用哪個部位捕食？', 'A': '觸手'},
    {'Q': '墨魚的血液是什麼顏色？', 'A': '藍色'},
    {'Q': '墨魚的智能與哪些動物相似？', 'A': '狗'},
    {'Q': '墨魚有沒有聽覺？', 'A': '有'}
]

def add_custom_reply(trigger, reply):
    custom_replies[trigger] = reply
    return f'嘿嘿~我學會新的回覆了哦！當你說"{trigger}"，我會說"{reply}"哦！'

def find_trigger(message):
    for trigger in custom_replies:
        if trigger in message:
            return trigger
    return None

def add_players(category, names):
    if category not in ['狗狗', '逆轉']:
        return
    existing = participants.get(category, {})
    added_names = []
    for name in names:
        if name not in existing:
            existing[name] = datetime.now()
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
    # 清空名单
    participants[category] = {}
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

def check_answer(reply_token, correct_answer, user_id):
    # 这里需要一个方式来获取最近的用户回答，可能需要使用全局变量或者数据库来存储用户回答
    recent_answer = get_recent_answer(user_id)  # 假设这个函数可以获取到用户的最近回答

    if recent_answer == correct_answer:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=f"恭喜答對了!! 墨魚啵一個^o^"))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=f"很遺憾，時間已到，答案是{correct_answer}"))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
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
    elif message == '/小秘書':
        reply_text = '''【小秘書指令說明】
        
        1. /新增 {類別} {名字1,名字2,...} - 將玩家加入到指定類別的名單中，可以一次新增多個玩家。
        2. /移除 {類別} {名字} - 從指定類別的名單中移除玩家，可以一次移除多個玩家。
        3. /清單 {類別} - 查看指定類別的名單。
        4. /抽獎 {類別} {數量} - 從指定類別的名單中抽取指定數量的玩家。
        類別只有「狗狗」跟「逆轉」技能書'''
       # 在原有的命令處理程式碼中新增以下部分
    elif message.startswith('/教育 '):
        _, trigger, reply = message.split(' ', 2)
        reply_text = add_custom_reply(trigger, reply)
    elif message.startswith('/墨魚知識大挑戰'):
        question, answer = random.choice(questions)['Q'], random.choice(questions)['A']
        reply_text = question
        #開始一個計時器，10秒後檢查答案
        timer = threading.Timer(10.0, check_answer, [event.reply_token, answer, user_id])
        timer.start()
    else:
        trigger = find_trigger(message)
        if trigger is not None:
            reply_text = custom_replies[trigger]


    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))
       
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
