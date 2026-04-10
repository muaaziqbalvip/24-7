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

# ================= DATABASE =================
DB_FILE = "mi_ai_users.json"

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

# ================= USER SYSTEM =================

def get_user(uid):
    if uid not in db:
        db[uid] = {
            "step": "name",
            "name": "",
            "phone": "",
            "email": "",
            "address": "",
            "mode": "gemini",
            "history": []
        }
        save_db(db)
    return db[uid]

def update(uid):
    save_db(db)

# ================= AI CORE =================

def ai_prompt(text):
    return f"""
Tum MI AI ho (Created by MUAAZ IQBAL).

RULES:
- Long detailed answer
- Step-by-step explanation
- Urdu + English mix
- Friendly tone

User:
{text}
"""

# ================= GEMINI =================

def gemini(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": ai_prompt(text)}]
            }]
        }
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
    return None

# ================= GROQ =================

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

# ================= OPENROUTER =================

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

# ================= SMART AI ROUTER =================

def smart_ai(text):
    for fn in [gemini, openrouter, groq]:
        res = fn(text)
        if res:
            return res
    return "⚠️ MI AI busy hai, try again."

# ================= SEARCH ENGINE =================

def search(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        return requests.get(url).text[:1500]
    except:
        return "Search failed"

# ================= MENU =================

def menu():
    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton("🤖 AI Chat", callback_data="ai"),
        types.InlineKeyboardButton("🌐 Search", callback_data="search")
    )

    kb.row(
        types.InlineKeyboardButton("📖 Story Mode", callback_data="story"),
        types.InlineKeyboardButton("📊 Poll", callback_data="poll")
    )

    kb.row(
        types.InlineKeyboardButton("👤 Profile", callback_data="profile"),
        types.InlineKeyboardButton("⚙ Mode", callback_data="mode")
    )

    return kb

# ================= START =================

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(
        m.chat.id,
        "🤖 MI AI MASTER SYSTEM\n👨‍💻 Created by MUAAZ IQBAL\n\nStart registration...",
        reply_markup=menu()
    )

# ================= REGISTRATION LOGIC =================

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = str(m.from_user.id)
    u = get_user(uid)
    text = m.text

    # ---------------- REGISTRATION FLOW ----------------
    if u["step"] == "name":
        u["name"] = text
        u["step"] = "phone"
        update(uid)
        bot.reply_to(m, "📱 Phone number send karo")
        return

    if u["step"] == "phone":
        u["phone"] = text
        u["step"] = "email"
        update(uid)
        bot.reply_to(m, "📧 Email send karo")
        return

    if u["step"] == "email":
        u["email"] = text
        u["step"] = "address"
        update(uid)
        bot.reply_to(m, "🏠 Address send karo")
        return

    if u["step"] == "address":
        u["address"] = text
        u["step"] = "done"
        update(uid)
        bot.reply_to(m, "✅ Registration complete! Ab MI AI ready hai 🤖")
        return

    # ---------------- PROFILE ----------------
    if text == "/profile":
        bot.reply_to(m, f"""
👤 USER PROFILE

Name: {u['name']}
Phone: {u['phone']}
Email: {u['email']}
Address: {u['address']}
""")
        return

    # ---------------- SEARCH ----------------
    if text.startswith("/search"):
        q = text.replace("/search", "")
        bot.reply_to(m, f"🌐 SEARCH RESULT:\n\n{search(q)}")
        return

    # ---------------- POLL ----------------
    if text.startswith("/poll"):
        q = text.replace("/poll", "")
        bot.send_poll(m.chat.id, q, ["Yes", "No", "Maybe"])
        return

    # ---------------- STORY MODE ----------------
    if "story" in text.lower():
        text = f"""
Cinematic detailed story likho:
{text}
"""

    # ---------------- AI RESPONSE ----------------
    bot.send_chat_action(m.chat.id, "typing")
    reply = smart_ai(text)

    bot.reply_to(m, f"""
🤖 MI AI RESPONSE

{reply}

👨‍💻 Created by MUAAZ IQBAL
""")

# ================= MEDIA =================

@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "🖼 Image received (vision upgrade needed for analysis)")

@bot.message_handler(content_types=['video'])
def video(m):
    bot.reply_to(m, "🎥 Video received")

@bot.message_handler(content_types=['voice'])
def voice(m):
    bot.reply_to(m, "🎤 Voice received (speech-to-text upgrade needed)")

# ================= RUN =================

print("🚀 MI AI MASTER SYSTEM RUNNING...")
bot.infinity_polling()