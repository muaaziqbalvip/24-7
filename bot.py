import telebot
import requests
import os
from telebot import types

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= MEMORY =================
users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "mode": "gemini"
        }
    return users[uid]

# ================= AI MODELS =================

def gemini_ai(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": text}]}]}
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
    return None


def groq_ai(text):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": text}]
        }
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None


def openrouter_ai(text):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": text}]
        }
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None


def smart_ai(text):
    for fn in [gemini_ai, openrouter_ai, groq_ai]:
        res = fn(text)
        if res:
            return res
    return "⚠️ MI AI busy hai, dobara try karo."

# ================= SEARCH =================

def web_search(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        r = requests.get(url).text
        return r[:1500]
    except:
        return "Search failed"

# ================= UI MENU =================

def main_menu():
    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
        types.InlineKeyboardButton("🌐 Search", callback_data="search")
    )

    kb.row(
        types.InlineKeyboardButton("🖼 Image", callback_data="img"),
        types.InlineKeyboardButton("🎥 Video", callback_data="video")
    )

    kb.row(
        types.InlineKeyboardButton("📊 Poll", callback_data="poll"),
        types.InlineKeyboardButton("⚙ AI Model", callback_data="model")
    )

    return kb

# ================= START =================

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(
        m.chat.id,
        "🤖 *MI AI ACTIVATED*\n\n👨‍💻 Created by MUAAZ IQBAL\n\nSelect option:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ================= CALLBACK =================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = str(call.from_user.id)
    u = get_user(uid)

    if call.data == "ai":
        bot.send_message(call.message.chat.id, "💬 Ab apna question bhejo (Urdu/Arabic/English)")

    if call.data == "search":
        bot.send_message(call.message.chat.id, "🌐 Use: /search query")

    if call.data == "img":
        bot.send_message(call.message.chat.id, "🖼 Image bhejo")

    if call.data == "video":
        bot.send_message(call.message.chat.id, "🎥 Video bhejo")

    if call.data == "poll":
        bot.send_message(call.message.chat.id, "📊 Use: /poll question")

    if call.data == "model":
        bot.send_message(call.message.chat.id, "⚙ Type: gemini / groq / openrouter")

# ================= TEXT HANDLER =================

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.from_user.id)
    u = get_user(uid)
    text = m.text

    # model switch
    if text.lower() in ["gemini", "groq", "openrouter"]:
        u["mode"] = text.lower()
        bot.reply_to(m, f"⚙ Model set: {text}")
        return

    # search
    if text.startswith("/search"):
        q = text.replace("/search", "").strip()
        result = web_search(q)
        bot.reply_to(m, f"🌐 SEARCH RESULT:\n\n{result}")
        return

    # poll
    if text.startswith("/poll"):
        q = text.replace("/poll", "").strip()
        bot.send_poll(m.chat.id, q or "MI AI Poll", ["Yes", "No", "Maybe"])
        return

    # AI chat
    bot.send_chat_action(m.chat.id, "typing")
    reply = smart_ai(text)

    final = f"""
🤖 *MI AI RESPONSE*

{reply}

✨ Urdu • Arabic • English Supported
👨‍💻 By MUAAZ IQBAL
"""

    bot.reply_to(m, final, parse_mode="Markdown")

# ================= MEDIA HANDLING =================

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "🖼 Image received by MI AI")

@bot.message_handler(content_types=['video'])
def video(m):
    bot.reply_to(m, "🎥 Video received by MI AI")

# ================= START =================

print("🚀 MI AI PRO RUNNING...")
bot.infinity_polling()