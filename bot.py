import telebot, threading, time
from telebot import types
from config import BOT_TOKEN, CHANNEL_ID
from ai_router import ask_ai
from memory import get_history, update_history

bot = telebot.TeleBot(BOT_TOKEN)
user_mode = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 Fast Mode","🧠 Pro Mode","🧹 Clear Memory")

    bot.reply_to(msg, "🤖 MI AI ULTRA ACTIVE", reply_markup=kb)

# ===== MODE =====
@bot.message_handler(func=lambda m: m.text in ["🚀 Fast Mode","🧠 Pro Mode","🧹 Clear Memory"])
def modes(msg):
    uid = msg.chat.id

    if msg.text == "🚀 Fast Mode":
        user_mode[uid] = "fast"
        bot.reply_to(msg,"⚡ Fast Mode ON")

    elif msg.text == "🧠 Pro Mode":
        user_mode[uid] = "pro"
        bot.reply_to(msg,"🧠 Pro Mode ON")

    elif msg.text == "🧹 Clear Memory":
        from memory import memory
        memory[uid] = []
        bot.reply_to(msg,"🧹 Memory Cleared")

# ===== CHAT =====
@bot.message_handler(func=lambda m: True)
def chat(msg):
    uid = msg.chat.id

    if msg.chat.type in ["group","supergroup"]:
        if not msg.text.lower().startswith("mi"):
            return

    mode = user_mode.get(uid,"fast")
    history = get_history(uid)

    update_history(uid,"user",msg.text)

    bot.send_chat_action(uid,"typing")

    reply, model = ask_ai(history, mode)

    update_history(uid,"model",reply)

    bot.reply_to(msg,f"{reply}\n\n[{model}]")

# ===== CHANNEL AUTO POST =====
def auto_post():
    while True:
        try:
            bot.send_message(CHANNEL_ID,"🔥 MI AI Auto Post Running")
        except:
            pass
        time.sleep(300)

threading.Thread(target=auto_post).start()

print("🚀 MI AI ULTRA LIVE")
bot.infinity_polling()