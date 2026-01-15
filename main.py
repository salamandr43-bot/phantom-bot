import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import telebot

# --- НАСТРОЙКИ ---
TOKEN = 'ТВОЙ_ТЕЛЕГРАМ_ТОКЕН'
CHAT_ID = 'ТВОЙ_CHAT_ID'
CHECK_INTERVAL = 600  # Проверка каждые 10 минут
SOURCE_URL = "https://www.oddsportal.com/matches/soccer/" # Пример источника

bot = telebot.TeleBot(TOKEN)

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # Запуск без окна
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Прикидываемся обычным пользователем
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    driver = uc.Chrome(options=options)
    return driver

def parse_games():
    driver = get_driver()
    games_found = []
    
    try:
        print(f"[*] Захожу на {SOURCE_URL}...")
        driver.get(SOURCE_URL)
        
        # Ждем, пока таблица с матчами появится (до 20 секунд)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'eventRow')))
        
        # Даем JS догрузить коэффициенты
        time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем блоки матчей (селекторы могут меняться, это база)
        rows = soup.find_all('div', class_='eventRow')
        
        for row in rows:
            try:
                # Извлекаем данные (примерная структура OddsPortal)
                teams = row.find('div', class_='event-name').text.strip()
                odds = row.find_all('div', class_='odds-now')
                
                o1 = odds[0].text.strip() if len(odds) > 0 else "-"
                ox = odds[1].text.strip() if len(odds) > 1 else "-"
                o2 = odds[2].text.strip() if len(odds) > 2 else "-"

                # Убираем "серьезный фильтр", оставляем только проверку на наличие кэфов
                if o1 != "-" and float(o1.replace(',', '.')) > 1.0:
                    game_info = f"⚽️ {teams}\n1: {o1} | X: {ox} | 2: {o2}"
                    games_found.append(game_info)
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"[!] Ошибка парсинга: {e}")
    finally:
        driver.quit()
    
    return games_found

def main():
    print("[+] Бот запущен и готов к поиску...")
    bot.send_message(CHAT_ID, "🚀 Бот запущен. Начинаю поиск матчей без жестких фильтров.")
    
    while True:
        print("[*] Начинаю сканирование...")
        matches = parse_games()
        
        if matches:
            print(f"[+] Найдено матчей: {len(matches)}")
            # Отправляем первые 5 матчей, чтобы не спамить в ТГ за раз
            for match in matches[:5]:
                bot.send_message(CHAT_ID, match)
        else:
            print("[-] Матчей пока нет или сработала защита.")
            # Можно отправить уведомление, если совсем глухо долгое время
            # bot.send_message(CHAT_ID, "⚠️ Данных нет. Проверь логи сервера.")

        print(f"[*] Сплю {CHECK_INTERVAL} секунд...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
