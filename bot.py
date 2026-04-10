import telebot
import requests
import os
from telebot import types

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

DB_BASE_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com/users"

bot = telebot.TeleBot(BOT_TOKEN)

# ================= FIREBASE =================
def update_user_data(uid, data):
    try:
        requests.patch(f"{DB_BASE_URL}/{uid}.json", json=data)
    except:
        pass

def get_user_data(uid):
    try:
        res = requests.get(f"{DB_BASE_URL}/{uid}.json")
        return res.json() or {}
    except:
        return {}

# ================= AI APIs =================

# ---- GEMINI ----
def ask_gemini(history):
    models = ["gemini-1.5-flash", "gemini-1.5-pro"]

    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            res = requests.post(url, json={"contents": history}, timeout=15)

            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text'], f"Gemini ({model})"
        except:
            continue

    return None, None

# ---- GROQ ----
def ask_groq(history):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        messages = []
        for h in history:
            role = "assistant" if h["role"] == "model" else "user"
            messages.append({"role": role, "content": h["parts"][0]["text"]})

        payload = {
            "model": "llama3-70b-8192",
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers, timeout=15)

        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"], "Groq (LLaMA3)"
    except:
        pass

    return None, None

# ---- OPENROUTER ----
def ask_openrouter(history):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        messages = []
        for h in history:
            role = "assistant" if h["role"] == "model" else "user"
            messages.append({"role": role, "content": h["parts"][0]["text"]})

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers, timeout=15)

        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"], "OpenRouter (GPT)"
    except:
        pass

    return None, None

# ================= SMART ROUTER =================
def ask_mi_ai(history, mode="fast"):

    if mode == "pro":
        engines = [ask_gemini, ask_groq, ask_openrouter]
    else:
        engines = [ask_gemini, ask_openrouter, ask_groq]

    for engine in engines:
        reply, name = engine(history)
        if reply:
            return reply, name

    return "⚠️ MI AI: Sab AI servers busy hain, dobara try karo.", "None"

# ================= BOT =================

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)

    update_user_data(uid, {
        "mode": "fast",
        "history": []
    })

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 Fast Mode", "🧠 Pro Mode", "🧹 Clear Memory")

    bot.send_message(
        message.chat.id,
        "🤖 *MI AI Activated*\n\nAsk anything...",
        parse_mode="Markdown",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: True)
def handle(message):
    uid = str(message.from_user.id)
    text = message.text

    if text == "🚀 Fast Mode":
        update_user_data(uid, {"mode": "fast"})
        bot.reply_to(message, "⚡ Fast Mode ON")
        return

    if text == "🧠 Pro Mode":
        update_user_data(uid, {"mode": "pro"})
        bot.reply_to(message, "🧠 Pro Mode ON")
        return

    if text == "🧹 Clear Memory":
        update_user_data(uid, {"history": []})
        bot.reply_to(message, "🧹 Memory Cleared")
        return

    bot.send_chat_action(message.chat.id, "typing")

    user = get_user_data(uid)
    history = user.get("history", [])
    mode = user.get("mode", "fast")

    if not isinstance(history, list):
        history = []

    history.append({"role": "user", "parts": [{"text": text}]})

    reply, model = ask_mi_ai(history, mode)

    if model != "None":
        history.append({"role": "model", "parts": [{"text": reply}]})
        history = history[-10:]
        update_user_data(uid, {"history": history})

    final = f"{reply}\n\n`[{model}]`"
    bot.reply_to(message, final, parse_mode="Markdown")

# ================= START =================
print("🚀 MI AI RUNNING (Multi-AI Routing Enabled)")
bot.infinity_polling()