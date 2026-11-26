import os
import time
import threading
import feedparser
import telebot
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(chr(95)*2 + "name" + chr(95)*2)

RSS_FEEDS = [
    "https://24.kg" + "/rss/",
    "https://kaktus.media" + "/?rss",
    "https://lenta.ru" + "/rss/news"
]

sent_links = set()
subscribers = set()

subscribers.add("-1005603755476")
subscribers.add("6572250940")
@bot.message_handler(commands=['start'])
def handle_start(message):
    subscribers.add(str(message.chat.id))
    bot.reply_to(message, "✅ Вы подписались на свежие новости! Новые посты будут приходить сюда автоматически. Чтобы отписаться, отправьте /stop")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    subscribers.discard(str(message.chat.id))
    bot.reply_to(message, "❌ Вы отписались от рассылки. Чтобы вернуться, нажмите /start")

def check_news():
    while True:
        for url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    if entry.link not in sent_links:
                        sent_links.add(entry.link)
                        text = f"📰 <b>{entry.title}</b>\n\n🔗 <a href='{entry.link}'>Читать полностью</a>"
                        for chat_id in list(subscribers):
                            try:
                                bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=False)
                            except Exception:
                                pass
            except Exception as e:
                print(f"Ошибка при чтении {url}: {e}")
        time.sleep(300)

@app.route('/')
def home():
    return "Бот работает!"

threading.Thread(target=check_news, daemon=True).start()
threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True), daemon=True).start()
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
