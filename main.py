import telebot
import cloudscraper
import time
import re
import os
import threading
import random
from flask import Flask

# --- НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ ---
TOKEN = '8530153013:AAHHejJ6a0UZ7PZOIR5ge8fDO6gmqYDQE9U'
USER_ID = 5919019209
DB_FILE = "database.txt"

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = telebot.TeleBot(TOKEN)
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
app = Flask('')
lock = threading.Lock()

# --- ВЕБ-СЕРВЕР (ЧТОБЫ НЕ СПАЛ) ---
@app.route('/')
def home():
    return "Phantom v47.0 is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- БАНК ---
def get_bank():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: return int(f.read().strip())
    except: pass
    return 17000

# --- ОТПРАВКА СООБЩЕНИЙ ---
def send_msg(text, markup=None):
    try:
        bot.send_message(USER_ID, text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
    except Exception as e:
        print(f"❌ Ошибка отправки в ТГ: {e}")

def create_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("✅ ЗАШЛО", callback_data="win"),
               telebot.types.InlineKeyboardButton("❌ МИМО", callback_data="loss"))
    markup.add(telebot.types.InlineKeyboardButton("💰 БАНК", callback_data="check_bank"))
    return markup

# --- ГЛАВНЫЙ СКАНЕР ---
def scan_logic(is_test_run=False):
    url = "https://www.flashscore.kz/x/feed/f_1_0_2_ru-kz_1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-fsign': 'SW9D1eZo',
        'referer': 'https://www.flashscore.kz/'
    }
    
    try:
        response = scraper.get(url, headers=headers, timeout=25)
        if response.status_code != 200:
            print(f"⚠️ Ошибка доступа к сайту: Код {response.status_code}")
            return

        blocks = response.text.split('~AA÷')
        print(f"📡 Скан: Найдено {len(blocks)-1} игр в лайве.")

        # ЕСЛИ ЭТО ПЕРВЫЙ ЗАПУСК - ШЛЕМ ТЕСТОВЫЙ СИГНАЛ
        if is_test_run and len(blocks) > 5:
            try:
                test_block = blocks[2] # Берем 2-й матч из списка
                h = re.search(r'AE\?([^\^]+)', test_block).group(1)
                a = re.search(r'AF\?([^\^]+)', test_block).group(1)
                send_msg(f"🧪 **ТЕСТ СВЯЗИ**\nВижу матч: {h} - {a}\n\nЕсли ты это читаешь — я вижу сайт! Начинаю работу по фильтрам.")
            except: pass
            return

        # ОБЫЧНЫЙ ПОИСК ПО ФИЛЬТРАМ
        for b in blocks:
            try:
                if 'ZA÷' in b: continue # Пропуск заголовков лиг
                
                # Парсинг данных
                h = re.search(r'AE\?([^\^]+)', b).group(1)
                a = re.search(r'AF\?([^\^]+)', b).group(1)
                sh = re.search(r'AG\?([^\^]+)', b).group(1)
                sa = re.search(r'AH\?([^\^]+)', b).group(1)
                
                # Время
                tm_raw = re.search(r'AC\?([^\^]+)', b)
                if not tm_raw: continue
                tm = int("".join(filter(str.isdigit, tm_raw.group(1))))

                # ФИЛЬТРЫ: 35-70 мин, разница <= 1
                if 35 <= tm <= 70 and abs(int(sh) - int(sa)) <= 1:
                    m_id = re.search(r'AA÷([^\^]+)', b).group(1)
                    
                    # Уникальность (чтобы не спамить один матч)
                    # (В простой версии опускаем сложную БД, надеемся на паузу 180сек)
                    
                    msg = (f"🔭 **ФАНТОМ: СИГНАЛ**\n"
                           f"⚔️ {h} — {a}\n"
                           f"⏱ {tm}' | Счет: **{sh}:{sa}**\n"
                           f"🔗 [1XBET](https://1xbet.kz/live/football)")
                    send_msg(msg, create_markup())
                    print(f"✅ ОТПРАВЛЕН СИГНАЛ: {h}-{a}")
            except: continue

    except Exception as e:
        print(f"❌ Критическая ошибка скана: {e}")

def scanner_loop():
    # 1. Сразу при старте делаем ТЕСТОВЫЙ скан (без фильтров)
    time.sleep(10) 
    scan_logic(is_test_run=True)
    
    # 2. Бесконечный цикл с фильтрами
    while True:
        time.sleep(180) # Раз в 3 минуты
        scan_logic(is_test_run=False)

# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "check_bank":
        bot.answer_callback_query(call.id, f"Банк: {get_bank()} ₸", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Ставка учтена (тест)")

# --- ЗАПУСК ---
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=scanner_loop, daemon=True).start()
    
    send_msg("🚀 **ФАНТОМ v47.0 (REBOOT)**\nЯ перезагрузился. Сейчас пришлю тестовый матч, чтобы ты видел, что я работаю.")
    print("🚀 BOT STARTED")
    
    try:
        bot.infinity_polling()
    except: pass
