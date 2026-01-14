import telebot
import cloudscraper
import time
import re
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TOKEN = '8530153013:AAHHejJ6a0UZ7PZOIR5ge8fDO6gmqYDQE9U'
USER_ID = 5919019209
DB_FILE = "database.txt"

bot = telebot.TeleBot(TOKEN)
scraper = cloudscraper.create_scraper()
app = Flask('')

@app.route('/')
def home():
    return "Phantom Bot is Alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def load_bank():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return int(f.read().strip())
    return 17000

current_bank = load_bank()

def send_alert(h, a, league, sh, sa, tm, m_id):
    msg = (f"🔭 **ОБЛАЧНЫЙ МОНИТОРИНГ**\n"
           f"🏆 {league}\n"
           f"⚔️ {h} — {a}\n"
           f"⏱ {tm}' | Счет: **{sh}:{sa}**\n\n"
           f"🔗 [1XBET](https://1xbet.kz/live/football)")

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("✅ ЗАШЛО", callback_data="win"),
               telebot.types.InlineKeyboardButton("❌ МИМО", callback_data="loss"))
    
    try:
        bot.send_message(USER_ID, msg, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    except: pass

def scan():
    url = "https://www.flashscore.kz/x/feed/f_1_0_2_ru-kz_1"
    headers = {'x-fsign': 'SW9D1eZo', 'referer': 'https://www.flashscore.kz/'}
    try:
        res = scraper.get(url, headers=headers, timeout=20)
        blocks = res.text.split('~AA÷')
        print(f"📡 Скан: {len(blocks)-1} игр.")
        curr_l = "Лига"
        for b in blocks:
            l_match = re.search(r'ZA÷([^\^]+)', b)
            if l_match: curr_l = l_match.group(1)
            try:
                m_id = re.search(r'AA÷([^\^]+)', b).group(1)
                h, a = re.search(r'AE\?([^\^]+)', b).group(1), re.search(r'AF\?([^\^]+)', b).group(1)
                sh, sa = re.search(r'AG\?([^\^]+)', b).group(1), re.search(r'AH\?([^\^]+)', b).group(1)
                tm = int("".join(filter(str.isdigit, re.search(r'AC\?([^\^]+)', b).group(1))))

                if abs(int(sh) - int(sa)) <= 1 and 35 <= tm <= 70:
                    send_alert(h, a, curr_l, sh, sa, tm, m_id)
            except: continue
    except Exception as e: print(f"Ошибка скана: {e}")

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.send_message(USER_ID, "🚀 **ФАНТОМ v46.4 ЗАПУЩЕН НА RENDER**\nОблако на связи, начинаю поиск матчей!")
    while True:
        scan()
        time.sleep(180)
