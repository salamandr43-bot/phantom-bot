def scan():
    print(f"📡 ТЕСТОВЫЙ СКАН запущен...")
    url = "https://www.flashscore.kz/x/feed/f_1_0_2_ru-kz_1"
    headers = {'x-fsign': 'SW9D1eZo', 'referer': 'https://www.flashscore.kz/'}
    try:
        res = scraper.get(url, headers=headers, timeout=20)
        blocks = res.text.split('~AA÷')
        print(f"🌍 Вижу в лайве: {len(blocks)-1} игр")
        
        # Берем ПЕРВЫЙ попавшийся матч и сразу шлем его в ТГ для теста
        if len(blocks) > 1:
            b = blocks[1]
            h = re.search(r'AE\?([^\^]+)', b).group(1)
            a = re.search(r'AF\?([^\^]+)', b).group(1)
            # Если это сообщение придет — значит бот НЕ СПИТ
            bot.send_message(USER_ID, f"🧪 ТЕСТ СВЯЗИ: Вижу матч {h} - {a}. Значит, данные идут!")
            
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
