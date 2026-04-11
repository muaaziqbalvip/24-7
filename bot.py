import telebot
import os
from telebot import types
from ai_engines import ask_all
from utils import format_reply
import threading
from scheduler import run_scheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_memory = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🤖 MI AI Activated\nAsk anything!")

# ===== MAIN CHAT =====
@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.chat.id

    if uid not in user_memory:
        user_memory[uid] = []

    history = user_memory[uid]

    history.append({"role":"user","parts":[{"text":msg.text}]})

    bot.send_chat_action(uid, "typing")

    reply, model = ask_all(history)

    history.append({"role":"model","parts":[{"text":reply}]})

    if len(history) > 10:
        history = history[-10:]

    user_memory[uid] = history

    bot.reply_to(msg, format_reply(reply, model))

# ===== GROUP AUTO REPLY =====
@bot.message_handler(content_types=['text'])
def group_reply(msg):
    if msg.chat.type in ["group","supergroup"]:
        if bot.get_me().username in msg.text:
            handle(msg)

# ===== CHANNEL AUTO POST =====
def start_scheduler():
    channel_id = "@your_channel_username"
    run_scheduler(bot, channel_id)

threading.Thread(target=start_scheduler).start()

print("🚀 MI AI LIVE")
bot.infinity_polling()