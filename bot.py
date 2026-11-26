import os
import time
import threading
import feedparser
import telebot
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

RSS_URLS = [
    "https://24.kg" + "/rss/",
    "https://kaktus.media" + "/?rss",
    "https://lenta.ru" + "/rss/news"
]

sent_links = set()
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(chr(95)*2 + "name" + chr(95)*2)

@app.route('/')
def home():
    return "Бот работает!"

def check_news():
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                sent_links.add(entry.link)
        except Exception:
            pass

    while True:
        if CHAT_ID:
            for url in RSS_URLS:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:3]:
                        if entry.link not in sent_links:
                            sent_links.add(entry.link)
                            text = f"📰 <b>{entry.title}</b>\n\n<a href='{entry.link}'>Читать подробнее</a>"
                            bot.send_message(CHAT_ID, text, parse_mode="HTML")
                            time.sleep(2)
                except Exception as e:
                    print(f"Ошибка: {e}")
        time.sleep(300)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет! Твой ID: {message.chat.id}\nВставь его в настройки хостинга (CHAT_ID).", parse_mode="Markdown")

threading.Thread(target=check_news, daemon=True).start()
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
