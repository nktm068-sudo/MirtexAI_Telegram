import datetime
import os
import random
import re
import threading
import time
from flask import Flask
import requests
import telebot

# 🔐 Бот забирает токен из Environment Variables на Render
API_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not API_TOKEN:
    print("❌ Ошибка: Переменная TELEGRAM_TOKEN не найдена в настройках Render!")
else:
    bot = telebot.TeleBot(API_TOKEN)

WEATHER_URL_SPACED = "h t t p s : / / w t t r . i n / ? f o r m a t = j 1"
# НОВАЯ ССЫЛКА НА ПЕРЕВОДЧИК
TRANSLATE_URL_SPACED = "h t t p s : / / t r a n s l a t e . g o o g l e a p i s . c o m / t r a n s l a t e _ a / s i n g l e ? c l i e n t = g t x & s l = r u & t l = e n & d t = t & q ="

# 🧠 ТВОЯ ПОЛНАЯ НЕЙРО-БАЗА ЗНАНИЙ
DATABASE = {
    "алмаз": {
        "correct_name": "прочный",
        "info": "это самый твёрдый камень на Земле! В реальной жизни им можно резать даже толстое стекло, а в Майнкрафте из него крафтят лучшую броню! 💎",
    },
    "эндермен": {
        "correct_name": "черный",
        "info": "это высокий монстр из Края, который умеет телепортироваться и воровать блоки. Главное — никогда не смотри ему прямо в глаза, а то он нанесёт много урона/убъёт!(носи тыкву на голове вырезанную) 👁️",
    },
    "видеокарта": {
        "correct_name": "мощная",
        "info": "она нужна, чтобы твой Роблокс и Майнкрафт выдавали много FPS! Она обрабатывает 3D-графику и передаёт картинку на монитор! 🎮",
    },
    "процессор": {
        "correct_name": "кремниевый",
        "info": "это самый главный мозг компьютера! Он состоит из миллиардов микроскопических переключателей (транзисторов) и делает все расчёты! 💻",
    },
    "лимон": {
        "correct_name": "кислый",
        "info": "в нём полным-полно лимонной кислоты и витамина C. Зато он круто защищает от простуды зимой! 🍋",
    },
    "шоколад": {
        "correct_name": "сладкий",
        "info": "его делают из горьких какао-бобов, но чтобы он стал вкусным, на фабрике туда бухают кучу сахара и молока! 🍫",
    },
    "кола": {
        "correct_name": "черная",
        "info": "в неё добавляют специальный краситель из жжёного сахара (карамель) и ортофосфорную кислоту. А сахара там аж 10 ложек на стакан! 🥤",
    },
    "бургер": {
        "correct_name": "вредный",
        "info": "в магазинном фастфуде очень много жирного соуса, соли и калорий, а витаминов почти нет. Если есть его каждый день, заболит живот! 🍔",
    },
    "воздух": {
        "correct_name": "прозрачный",
        "info": "мы его не видим, потому что молекулы газов в нём находятся очень далеко друг от друга и свободно пропускают свет! 💨",
    },
    "атмосфера": {
        "correct_name": "прозрачная",
        "info": "она состоит из невидимых газов — азота и кислорода. Она защищает нас от падения метеоритов и космического холода! 🌍",
    },
    "луна": {
        "correct_name": "круглая",
        "info": "это огромный каменистый шар и спутник Земли. Из-за мощной гравитации она сжалась в форму шара ещё миллиарды лет назад! 🌕",
    },
    "крипер": {
        "correct_name": "зеленый",
        "info": "создатель Майнкрафта Маркус Перссон (Нотч) случайно перепутал длину и высоту тела у модели свиньи, и получился этот легендарный монстр! 💣",
    },
    "кот": {
        "correct_name": "мурчит",
        "info": "кошачий мозг посылает сигналы к мышцам гортани, они начинают быстро дрожать, и получается такой уютный вибрирующий звук! 🐱",
    },
    "океан": {
        "correct_name": "соленый",
        "info": "дожди миллиарды лет вымывали из камней и скал минералы и соли, а реки уносили всё это в море. Вода испарялась, а соль оставалась! 🌊",
    },
    "солнце": {
        "correct_name": "горячее",
        "info": "это огромный раскалённый газовый шар, внутри которого каждую секунду происходит ядерный взрыв, выделяющий кучу тепла! ☀️",
    },
    "небо": {
        "correct_name": "голубое",
        "info": "солнечный свет состоит из всех цветов радуги. Синие лучи сталкиваются с воздухом и рассеиваются во все стороны сильнее остальных! 🌌",
    },
    "арбуз": {
        "correct_name": "ягода",
        "info": "он растет на земле и у него сочная мякоть с семечками внутри!",
    },
    "трава": {
        "correct_name": "зеленая",
        "info": "в её клетках есть хлорофилл. Он работает как солнечная батарея, поглощает красный свет, а зелёный цвет отражает нам в глаза! 🌿",
    },
    "огурец": {
        "correct_name": "зеленый",
        "info": "он состоит на 95% из воды и отлично хрустит в салате.",
    },
}
user_chat_history = {}

# --- НЕОБХОДИМАЯ ЧАСТЬ ДЛЯ RENDER (ВЕБ-СЕРВЕР) ---
app = Flask("")


@app.route("/")
def home():
    return "🤖 Миртекс работает на Render!"


def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


# ------------------------------------------------


def get_clean_url(spaced_url):
    return spaced_url.replace(" ", "")


def check_math(text):
    clean = re.sub(r"[^0-9+\-*/(). ]", "", text).strip()
    if len(clean) >= 3 and any(char.isdigit() for char in clean):
        try:
            result = eval(clean, {"__builtins__": None}, {})
            if isinstance(result, (int, float)):
                return result
        except Exception:
            return None
    return None

def fetch_weather(city_name_ru=""):
    try:
        # 🏙️ Если город не написан, берём по умолчанию Москву
        if not city_name_ru:
            city_name_ru = "Москва"
            city_name_en = "Moscow"
        else:
            city_name_ru = city_name_ru.strip().capitalize()
            # Очищаем секретную ссылку переводчика от пробелов перед запросом
            clean_translate_url = get_clean_url(TRANSLATE_URL_SPACED) + city_name_ru
            tr_response = requests.get(clean_translate_url, timeout=5)
            # Вытаскиваем чистое английское слово из ответа Google
            city_name_en = tr_response.json()

        # Подставляем переведённый город в ссылку погоды
        clean_url = get_clean_url(WEATHER_URL_SPACED).replace("/?", f"/{city_name_en}?")
        response = requests.get(clean_url, timeout=5)
        data = response.json()
        current = data["current_condition"]
        temp = current["temp_C"]

        desc = current.get("weatherDesc", [{"value": "Неизвестно"}])["value"]
        if "lang_ru" in current and current["lang_ru"]:
            desc = current["lang_ru"]["value"]

        return f"🌤 Погода в городе *{city_name_ru}*:\n🌡 Температура: *{temp}°C*\n📝 На улице: *{desc}*"
    except Exception as e:
        print(f"Ошибка погоды: {e}")
        return "❌ Не удалось найти такой город. Проверь, правильно ли написано название!"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    welcome_text = (
        "👋 **Привет! Я твой умный бот Миртекс!** 🧠✨\n\n"
        "С первым днём лета и началом каникул! ☀️\n"
        "Я умею считать примеры, показывать время, загружать погоду и спорить на разные темы! 🎮💎\n\n"
        "Попробуй написать мне: *какая погода* или *крипер розовый*! 😎"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    query = message.text
    text = query.lower().strip()

    # Показываем анимацию обработки запроса
    loading_msg = bot.send_message(
        message.chat.id, "🧠 _Миртекс обрабатывает запрос..._", parse_mode="Markdown"
    )
    time.sleep(0.5)

    ai_result = ""

    # 🎁 СЕКРЕТНАЯ КОМАНДА НА ДЕНЬ РОЖДЕНИЯ АВТОРА (СТРОГО 2 ИЮНЯ!)
    if "2 june" in text or "2 июня" in text:
        ai_result = "🎉🎂🎈 *УРА-А-А-А!* Сегодня, 2 июня, День рождения у создателя этого крутого бота! *Поздравляем Никиту с 9-летием!* 🥳 Пожелаем ему тонну счастья, бесконечных каникул и чтобы новенький Xbox Series S работал без багов и тащил все игры на ультрах! Напиши Никите в ЛС и поздравь его! 🎮🔥"

    # 1. Калькулятор
    if ai_result == "":
        math_result = check_math(text)
        if math_result is not None:
            ai_result = f"🧮 Ответ равен: *{math_result}*"

    # 2. Время
    if (
        ai_result == ""
        and any(word in text for word in ["время", "час", "сколько время"])
    ):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        ai_result = f"⏰ Время на часах: *{now}*"

    # 3. Погода (Супер-умный разбор фразы и поиск любого города!)
    if (
        ai_result == ""
        and any(word in text for word in ["погода", "погоду", "на улице"])
    ):
        chosen_city = ""
        # Очищаем текст от всех возможных мусорных слов
        clean_text = text
        for trash in [
            "погода",
            "погоду",
            "на улице",
            "какая",
            "какой",
            "сейчас",
            "в",
            "на",
            "город",
            "городе",
        ]:
            clean_text = clean_text.replace(trash, "")

        # Убираем лишние пробелы по краям, теперь там осталось ТОЛЬКО имя города!
        chosen_city = clean_text.strip()

        ai_result = fetch_weather(chosen_city)

    # 4. База знаний
    if ai_result == "":
        found_topic = ""
        for key in DATABASE:
            if key in text:
                found_topic = key
                break

        if found_topic != "":
            topic_data = DATABASE[found_topic]
            correct_word = topic_data["correct_name"]
            main_info = topic_data["info"]

            # Проверяем правильность слов (учитываем буквы е/ё)
            has_correct_word = correct_word in text
            if correct_word == "зеленая" and "зелёная" in text:
                has_correct_word = True
            if correct_word == "соленый" and "солёный" in text:
                has_correct_word = True

            if has_correct_word:
                ai_result = f"🤖 Да, всё верно! Ведь {main_info}"
            else:
                ai_result = f"Нет, вообще-то {found_topic} — *{correct_word}*, и вот почему: {main_info}"

    # 5. Баги и Рецепты
    if ai_result == "":
        if any(word in text for word in ["ошибка", "баг", "сломалось"]):
            ai_result = "🛠️ Не беспокойтесь, это поправимо. Рекомендую проверить закрытие всех скобок и правильность кавычек в репозитории на GitHub. Ваш код обязательно заработает!"
        elif any(
            word in text
            for word in ["рецепт", "приготовить", "кушать", "еда", "пицца", "блин"]
        ):
            if "пицца" in text or "пиццы" in text:
                ai_result = "🍕 *Рецепт mini-пиццы:* возьмите батон, смажьте кетчупом, положите ломтик колбасу, сыр и запекайте в микроволновой печи в течение 1 минуты."
            else:
                ai_result = "🥞 *Рецепт классических блинчиков:* смешайте 1 яйцо, 1 стакан молока и 1 стакан муки. Добавьте немного сахара и выпекайте на разогретой сковороде."

    # 6. Умный и вежливый собеседник (Вместо дворового сленга!)
    if ai_result == "":
        current_time = time.time()

        if (
            user_id not in user_chat_history
            or (current_time - user_chat_history[user_id]["last_time"]) > 7200
        ):
            user_chat_history[user_id] = {
                "hello_count": 0,
                "last_time": current_time,
            }

        words_hello = ["привет", "привёт", "хай", "ку", "салам", "здарова", "йо"]
        is_hello = any(word in text for word in words_hello)

        if is_hello:
            user_chat_history[user_id]["hello_count"] += 1
            user_chat_history[user_id]["last_time"] = current_time

        hello_count = user_chat_history[user_id]["hello_count"]
        is_status = any(
            word in text
            for word in ["как дела", "как жизнь", "че как", "как ты", "настроение", "как сам"]
        )

        if is_status:
            ai_result = random.choice([
                "У меня всё функционирует отлично, виртуальные системы работают на полную мощность! Как ваши успехи? 🚀",
                "Благодарю за интерес, я нахожусь в режиме стабильной работы и готов к вычислениям. А как идут дела у вас? 💻",
                "Настроение прекрасное! Готов помочь вам разобраться в любых научных темах и сложных вопросов. 🧠",
            ])
        elif is_hello:
            if hello_count > 1:
                ai_result = random.choice([
                    "Мы с вами уже поздоровались. Рад продолжать наше интеллектуальное общение! 😊",
                    "Приветствую вас повторно! Моя оперативная память зафиксировала наше приветствие. 👋",
                ])
            else:
                ai_result = "👋 Здравствуйте! Я ваш персональный интеллектуальный ассистент Миртекс. Поздравляю вас с началом лета и долгожданных каникул! Чем могу помочь вам сегодня? ☀️"
        elif "новости" in text or "новость" in text:
            ai_result = "📰 *Главные новости на сегодня:* На дворе прекрасное 1 июня — первый день лета и Всемирный день защиты детей! В Кемерово стоит отличная солнечная погода, а до одного очень важного события и крутого Xbox осталось совсем чуть-чуть! ☀️🎮"
        else:
            ai_result = random.choice([
                "Это весьма интересная мысль. Не могли бы вы рассказать об этом подробнее? 📝",
                "Ваше сообщение принято к сведению. Мои алгоритмы полностью согласны с этой точкой зрения! 🤖",
                "Очень занимательная тема для обсуждения. Каков будет наш следующий шаг? 🧠",
            ])

    # 🛑 Удаляем анимацию загрузки перед выдачей ответа
    bot.delete_message(message.chat.id, loading_msg.message_id)
    bot.send_message(message.chat.id, ai_result, parse_mode="Markdown")


def ping_server():
    while True:
        try:
            requests.get("https://mirtexai-telegram.onrender.com/", timeout=300)
        except:
            pass
        time.sleep(960)


if __name__ == "__main__" and API_TOKEN:
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=ping_server, daemon=True).start()
    print("🤖 Миртекс запущен!")
    bot.infinity_polling()
