import telebot
import requests
import json
import time
from telebot import types

# --- 1. Configurations ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"
# فائر بیس یو آر ایل کے آخر میں .json لگانا ضروری ہے REST API کے لیے
DB_BASE_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com/users"

bot = telebot.TeleBot(BOT_TOKEN)

# --- 2. Firebase REST Functions (No Auth Required) ---
def update_user_data(uid, data):
    url = f"{DB_BASE_URL}/{uid}.json"
    try:
        requests.patch(url, json=data)
    except: pass

def get_user_data(uid):
    url = f"{DB_BASE_URL}/{uid}.json"
    try:
        response = requests.get(url)
        return response.json() or {}
    except: return {}

# --- 3. Gemini AI Logic (Direct API) ---
def ask_ai_direct(prompt, model_name="gemini-1.5-flash"):
    # اگر ماڈل کا نام غلط ہو تو اسے درست کریں
    if "flash" not in model_name and "pro" not in model_name:
        model_name = "gemini-1.5-flash"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ AI Service Busy. Try again later."

# --- 4. Bot Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # فائر بیس میں ڈیٹا محفوظ کرنا
    update_user_data(uid, {
        "name": message.from_user.first_name,
        "username": message.from_user.username,
        "mode": "gemini-1.5-flash"
    })

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Fast Mode", "🧠 Pro Thinking", "🔍 AI Search")
    bot.send_message(message.chat.id, f"Assalam-o-Alaikum {message.from_user.first_name}!\n\n**MI AI** is now Online. No more errors. 🔥\n\nChoose a mode and ask anything!", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    text = message.text
    
    # موڈ تبدیل کرنے کی لاجک
    if text == "🚀 Fast Mode":
        update_user_data(uid, {"mode": "gemini-1.5-flash"})
        bot.reply_to(message, "⚡ Switched to **Fast Thinking**.")
        return
    elif text == "🧠 Pro Thinking":
        update_user_data(uid, {"mode": "gemini-1.5-pro"})
        bot.reply_to(message, "🧠 Switched to **Pro Thinking (Deep Analysis)**.")
        return
    elif text == "🔍 AI Search":
        update_user_data(uid, {"mode": "gemini-1.5-flash"})
        bot.reply_to(message, "🔍 Search Mode Active. Send your query.")
        return

    # موجودہ ڈیٹا حاصل کریں
    user_data = get_user_data(uid)
    mode = user_data.get("mode", "gemini-1.5-flash")
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # AI سے جواب
    response = ask_ai_direct(text, mode)
    bot.reply_to(message, response, parse_mode="Markdown")

# --- 5. Start Polling ---
print("MI AI Running on REST API Mode (No Files Needed)...")
bot.infinity_polling()
