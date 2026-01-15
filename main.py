import os
import time
import threading
import requests
import telebot
from flask import Flask

# --- КОНФИГУРАЦИЯ ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# 1. Мини-сервер для Render (чтобы не было ошибки Port Scan)
@app.route('/')
def hello():
    return "Bot is running", 200

def run_flask():
    # Render всегда использует порт 10000
    app.run(host='0.0.0.0', port=10000)

# 2. Функция поиска игр (БЕЗ браузера, через легкий запрос)
def check_games():
    try:
        # Используем открытый API или простой источник данных
        # Для примера берем список матчей (можешь заменить на свой URL)
        url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?regions=eu&apiKey=YOUR_API_KEY"
        # Если ключа нет, пока просто имитируем поиск, чтобы проверить связь
        print("[*] Сканирую матчи через Requests...")
        
        # Здесь будет логика обработки JSON
        return [] # Пока возвращаем пусто, чтобы не спамить
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return []

# 3. Основная логика бота
def bot_polling():
    print("🚀 Бот стартовал")
    bot.send_message(CHAT_ID, "✅ Бот запущен! Теперь Render его не отключит.")
    
    while True:
        try:
            # Твой цикл поиска игр
            games = check_games()
            if games:
                for game in games:
                    bot.send_message(CHAT_ID, game)
            
            # Спим 10 минут
            time.sleep(600)
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Запускаем бота
    bot_polling()
