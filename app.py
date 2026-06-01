import os
import re
import datetime
import requests
import telebot
from flask import Flask
import threading

# 1. ПОДКЛЮЧЕНИЕ ТЕЛЕГРАМ-БОТА ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# На Render ты тоже сможешь спрятать ключ в Environment Variables!
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)

WEATHER_URL_SPACED = "h t t p s : / / w t t r . i n / ? f o r m a t = j 1"

def get_clean_url(spaced_url):
    return spaced_url.replace(" ", "")

# ====================================================================
# 2. ТВОИ НАСТОЯЩИЕ ФУНКЦИИ ИИ
# ====================================================================
def check_math(text):
    clean = re.sub(r'[^0-9+\-*/(). ]', '', text).strip()
    if len(clean) >= 3 and any(char.isdigit() for char in clean):
        try:
            result = eval(clean, {"__builtins__": None}, {})
            if isinstance(result, (int, float)):
                return round(result, 4)
        except:
            return None
    return None

def fetch_weather():
    try:
        clean_url = get_clean_url(WEATHER_URL_SPACED)
        response = requests.get(clean_url, timeout=5)
        data = response.json()
        current = data['current_condition'][0]
        temp = current['temp_C']
        desc = current['lang_ru'][0]['value'] if 'lang_ru' in current else current['weatherDesc'][0]['value']
        return f"🌤 Погода в твоём городе:\n🌡 Температура: {temp}°C\n📝 На улице: {desc}"
    except:
        return "❌ Не удалось загрузить погоду. Проверь сеть."

def start_local_ai(user_text):
    text = user_text.lower().strip()
    if text == "очистить":
        return "[СИСТЕМА]: История чата очищена в памяти бота."
    
    math_result = check_math(text)
    if math_result is not None:
        return f"🧮 Ответ равен: {math_result}"

    time_words = ["время", "час", "сколько время", "сколько часов"]
    if any(word in text for word in time_words):
        now = datetime.datetime.now()
        return f"⏰ Время на часах: {now.strftime('%H:%M:%S')}"

    weather_words = ["погода", "погоду", "на улице"]
    if any(word in text for word in weather_words):
        return fetch_weather()

    return "Хмм, интересная мысль! Попробуй спросить про 'погоду', 'время' или напиши пример (например: 5+5)!"

# ====================================================================
# 3. ТЕЛЕГРАМ ОБРАБОТЧИК
# ====================================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Миртекс AI успешно запущен на Render!\n\nНапиши мне: 'погода', 'время' или любой математический пример.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if len(message.text) > 10000:
        bot.reply_to(message, "Отрезано! Текст больше 10 000 символов.")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    reply = start_local_ai(message.text)
    bot.reply_to(message, reply)

# Запуск бота в отдельном потоке
if BOT_TOKEN:
    threading.Thread(target=bot.infinity_polling, daemon=True).start()

# ====================================================================
# 4. ВЕБ-СЕРВЕР ДЛЯ РЕНДЕРА (Чтобы хостинг не отключал бота)
# ====================================================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Миртекс AI успешно работает на сервере Render!"

if __name__ == "__main__":
    # Render сам передает порт через переменную среды PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
