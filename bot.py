import telebot
import requests
import os
import json
from telebot import types

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= LOCAL DATABASE =================
DB_FILE = "users.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

db = load_db()

# ================= USER REGISTRATION =================

def get_user(uid):
    if uid not in db:
        db[uid] = {
            "step": "name",
            "name": "",
            "phone": "",
            "email": "",
            "address": "",
            "mode": "gemini"
        }
        save_db(db)
    return db[uid]

# ================= AI PROMPTS =================

def ai_prompt(text):
    return f"""
Tum MI AI Ultra Pro Max ho (Created by MUAAZ IQBAL).

RULES:
- Long detailed answer
- Urdu + English mix
- Deep explanation
- Friendly tone

User:
{text}
"""

# ================= AI MODELS =================

def gemini(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": ai_prompt(text)}]}]}
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
            "messages": [{"role": "user", "content": ai_prompt(text)}]
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
            "messages": [{"role": "user", "content": ai_prompt(text)}]
        }
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None


def smart_ai(text):
    for fn in [gemini, openrouter, groq]:
        r = fn(text)
        if r:
            return r
    return "⚠️ MI AI busy hai"

# ================= MENU =================

def menu():
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("🤖 AI", callback_data="ai"),
        types.InlineKeyboardButton("🌐 Search", callback_data="search")
    )
    kb.row(
        types.InlineKeyboardButton("📖 Story", callback_data="story"),
        types.InlineKeyboardButton("👤 Profile", callback_data="profile")
    )
    return kb

# ================= START =================

@bot.message_handler(commands=['start'])
def start(m):
    uid = str(m.from_user.id)
    u = get_user(uid)

    bot.send_message(
        m.chat.id,
        "🤖 MI AI ULTRA PRO MAX\n\n👨‍💻 Created by MUAAZ IQBAL\n\nWelcome!\nFirst register yourself.",
        reply_markup=menu()
    )

# ================= REGISTRATION SYSTEM =================

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.from_user.id)
    u = get_user(uid)
    text = m.text

    # ---------------- REGISTRATION FLOW ----------------
    if u["step"] == "name":
        u["name"] = text
        u["step"] = "phone"
        save_db(db)
        bot.reply_to(m, "📱 Ab apna PHONE number bhejo")
        return

    if u["step"] == "phone":
        u["phone"] = text
        u["step"] = "email"
        save_db(db)
        bot.reply_to(m, "📧 Ab apna EMAIL bhejo")
        return

    if u["step"] == "email":
        u["email"] = text
        u["step"] = "address"
        save_db(db)
        bot.reply_to(m, "🏠 Ab apna ADDRESS bhejo")
        return

    if u["step"] == "address":
        u["address"] = text
        u["step"] = "done"
        save_db(db)
        bot.reply_to(m, "✅ Registration complete!\nAb MI AI ready hai 🤖")
        return

    # ---------------- PROFILE ----------------
    if text == "/profile":
        bot.reply_to(m, f"""
👤 PROFILE:

Name: {u['name']}
Phone: {u['phone']}
Email: {u['email']}
Address: {u['address']}
""")
        return

    # ---------------- SEARCH ----------------
    if text.startswith("/search"):
        q = text.replace("/search", "")
        url = f"https://duckduckgo.com/html/?q={q}"
        res = requests.get(url).text[:1200]
        bot.reply_to(m, f"🌐 SEARCH RESULT:\n\n{res}")
        return

    # ---------------- AI CHAT ----------------
    bot.send_chat_action(m.chat.id, "typing")
    reply = smart_ai(text)

    bot.reply_to(m, f"""
🤖 MI AI RESPONSE

{reply}

👨‍💻 By MUAAZ IQBAL
""")

# ================= MEDIA =================

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "🖼 Image received (Vision upgrade needed)")

@bot.message_handler(content_types=['video'])
def video(m):
    bot.reply_to(m, "🎥 Video received")

@bot.message_handler(content_types=['voice'])
def voice(m):
    bot.reply_to(m, "🎤 Voice received")

# ================= RUN =================

print("🚀 MI AI ULTRA PRO MAX RUNNING...")
bot.infinity_polling()