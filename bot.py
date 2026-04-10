import telebot
import requests
import os
from telebot import types

# ================= MI AI CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= MEMORY =================
users = {}

def user(uid):
    if uid not in users:
        users[uid] = {
            "mode": "gemini"
        }
    return users[uid]

# ================= PROMPTS =================

def base_prompt(text):
    return f"""
Tum MI AI ho (Created by MUAAZ IQBAL).

RULES:
- Long detailed answer do
- Urdu + English + Arabic style allowed
- Deep explanation
- Friendly tone
- Step-by-step thinking

User:
{text}
"""

def story_prompt(text):
    return f"""
Tum MI AI Story Writer ho.

RULES:
- Cinematic story likho
- Chapters use karo
- Emotions + scenes detail me do
- Urdu + English mix
- Ending strong ho

Story request:
{text}
"""

# ================= AI MODELS =================

def gemini(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": base_prompt(text)}]}]}
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
    return None


def groq(text):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": base_prompt(text)}]
        }
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None


def openrouter(text):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": base_prompt(text)}]
        }
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None


def smart_ai(text):
    for fn in [gemini, openrouter, groq]:
        res = fn(text)
        if res:
            return res
    return "⚠️ MI AI busy hai"

# ================= SEARCH =================

def search(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        return requests.get(url).text[:1200]
    except:
        return "Search error"

# ================= UI MENU =================

def menu():
    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
        types.InlineKeyboardButton("🌐 Search", callback_data="search")
    )

    kb.row(
        types.InlineKeyboardButton("📖 Story Mode", callback_data="story"),
        types.InlineKeyboardButton("🧠 Deep Think", callback_data="deep")
    )

    kb.row(
        types.InlineKeyboardButton("⚙ AI Model", callback_data="model"),
        types.InlineKeyboardButton("📊 Poll", callback_data="poll")
    )

    return kb

# ================= START =================

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(
        m.chat.id,
        "🤖 *MI AI ACTIVATED*\n\n👨‍💻 Created by MUAAZ IQBAL\n\nSelect option:",
        parse_mode="Markdown",
        reply_markup=menu()
    )

# ================= CALLBACK =================

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = str(c.from_user.id)
    u = user(uid)

    if c.data == "ai":
        bot.send_message(c.message.chat.id, "💬 Send your question")

    if c.data == "search":
        bot.send_message(c.message.chat.id, "🌐 Use /search query")

    if c.data == "story":
        bot.send_message(c.message.chat.id, "📖 Send story topic")

    if c.data == "deep":
        bot.send_message(c.message.chat.id, "🧠 Deep thinking ON")

    if c.data == "model":
        bot.send_message(c.message.chat.id, "⚙ Type: gemini / groq / openrouter")

    if c.data == "poll":
        bot.send_message(c.message.chat.id, "📊 Use /poll question")

# ================= TEXT HANDLER =================

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.from_user.id)
    u = user(uid)
    text = m.text

    # model switch
    if text.lower() in ["gemini", "groq", "openrouter"]:
        u["mode"] = text.lower()
        bot.reply_to(m, f"⚙ Mode set: {text}")
        return

    # search
    if text.startswith("/search"):
        q = text.replace("/search", "")
        bot.reply_to(m, f"🌐 SEARCH:\n\n{search(q)}")
        return

    # poll
    if text.startswith("/poll"):
        q = text.replace("/poll", "")
        bot.send_poll(m.chat.id, q, ["Yes", "No", "Maybe"])
        return

    # STORY MODE trigger
    if "story" in text.lower():
        reply = smart_ai(story_prompt(text))
    else:
        reply = smart_ai(text)

    final = f"""
🤖 MI AI RESPONSE

{reply}

👨‍💻 By MUAAZ IQBAL
"""
    bot.reply_to(m, final, parse_mode="Markdown")

# ================= MEDIA =================

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "🖼 MI AI received image (Vision upgrade needed for analysis)")

@bot.message_handler(content_types=['video'])
def video(m):
    bot.reply_to(m, "🎥 Video received by MI AI")

@bot.message_handler(content_types=['voice'])
def voice(m):
    bot.reply_to(m, "🎤 Voice received (speech-to-text upgrade needed)")

# ================= RUN =================

print("🚀 MI AI FULL SYSTEM RUNNING...")
bot.infinity_polling()