import os
import time
import telebot
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- КОНФИГУРАЦИЯ (Берем из настроек Render) ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Проверка наличия ключей перед запуском
if not TOKEN or not CHAT_ID:
    print("[!] ОШИБКА: Проверь вкладку Environment в Render. TELEGRAM_TOKEN или CHAT_ID не найдены.")
    exit(1)

bot = telebot.TeleBot(TOKEN)

def get_driver():
    """Настройка браузера для работы в условиях Render (512MB RAM)"""
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Указываем путь к Chrome, который установил наш скрипт render-build.sh
    chrome_path = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(chrome_path):
        options.binary_location = chrome_path
    
    # Прикидываемся обычным пользователем
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    return uc.Chrome(options=options)

def parse_odds():
    """Парсинг матчей с OddsPortal (пример)"""
    driver = None
    matches_data = []
    
    try:
        driver = get_driver()
        print("[*] Подключаюсь к источнику данных...")
        driver.get("https://www.oddsportal.com/matches/soccer/")
        
        # Ждем загрузки основного контента (до 20 секунд)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'eventRow')))
        
        # Даем JS время отрисовать коэффициенты
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rows = soup.find_all('div', class_='eventRow')
        
        for row in rows:
            try:
                # Извлекаем названия команд и коэффициенты
                event_name = row.find('div', class_='event-name').text.strip()
                odds_elements = row.find_all('div', class_='odds-now')
                
                if len(odds_elements) >= 3:
                    o1 = odds_elements[0].text.strip()
                    ox = odds_elements[1].text.strip()
                    o2 = odds_elements[2].text.strip()
                    
                    # Формируем сообщение (без жестких фильтров по твоему запросу)
                    matches_data.append(f"⚽️ {event_name}\nП1: {o1} | X: {ox} | П2: {o2}")
            except:
                continue
                
    except Exception as e:
        print(f"[!] Ошибка браузера: {e}")
    finally:
        if driver:
            driver.quit() # Важно для экономии памяти на Render
            
    return matches_data

def main():
    print("[+] Бот запущен. Начинаю цикл мониторинга...")
    bot.send_message(CHAT_ID, "🚀 Бот 'FINK' успешно запущен на Render! Начинаю поиск игр.")
    
    while True:
        try:
            print("[*] Запуск сканирования матчей...")
            matches = parse_odds()
            
            if matches:
                print(f"[+] Найдено {len(matches)} матчей.")
                # Отправляем топ-5 актуальных матчей
                for m in matches[:5]:
                    bot.send_message(CHAT_ID, m)
            else:
                print("[-] Новых подходящих игр не найдено.")
            
            # Интервал проверки (например, каждые 15 минут, чтобы не забанили)
            print("[*] Сон 15 минут...")
            time.sleep(900)
            
        except Exception as e:
            print(f"[!] Критическая ошибка в цикле: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
