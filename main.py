import telebot
import cloudscraper
import time
import re
import os
import threading
from flask import Flask

# --- НАСТРОЙКИ ---
TOKEN = '8530153013:AAHHejJ6a0UZ7PZOIR5ge8fDO6gmqYDQE9U'
USER_ID = 5919019209
DB_FILE = "database.txt"

bot = telebot.TeleBot(TOKEN)
scraper = cloudscraper.create_scraper()
app = Flask('')

@app.route('/')
def home(): return "Phantom Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_bank():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: return int(f.read().strip())
    except: pass
    return 17000

def scanner_loop():
    print("🤖 Сканер запущен...")
    while True:
        try:
            url = "https://www.flashscore.kz/x/feed/f_1_0_2_ru-kz_1"
            headers = {'x-fsign': 'SW9D1eZo', 'referer': 'https://www.flashscore.kz/'}
            res = scraper.get(url, headers=headers, timeout=30)
            blocks = res.text.split('~AA÷')
            print(f"📡 Скан {time.strftime('%H:%M')}: {len(blocks)-1} игр")
            for b in blocks:
                try:
                    h, a = re.search(r'AE\?([^\^]+)', b).group(1), re.search(r'AF\?([^\^]+)', b).group(1)
                    sh, sa = re.search(r'AG\?([^\^]+)', b).group(1), re.search(r'AH\?([^\^]+)', b).group(1)
                    tm = int("".join(filter(str.isdigit, re.search(r'AC\?([^\^]+)', b).group(1))))
                    if 35 <= tm <= 70 and abs(int(sh) - int(sa)) <= 1:
                        msg = f"🔭 **ФАНТОМ**\n⚔️ {h} — {a}\n⏱ {tm}' | Счет: **{sh}:{sa}**"
                        bot.send_message(USER_ID, msg, parse_mode='Markdown')
                except: continue
        except: pass
        time.sleep(180)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=scanner_loop, daemon=True).start()
    print("🚀 ФАНТОМ v46.5 в эфире!")
    bot.infinity_polling()
