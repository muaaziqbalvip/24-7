import telebot
import requests
import json
import firebase_admin
from firebase_admin import db
from telebot import types

# --- 1. Configurations ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"
DB_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com"

# --- 2. Firebase Connection (Safe Mode) ---
if not firebase_admin._apps:
    # بغیر کسی سرٹیفکیٹ فائل کے کنیکٹ کرنے کا طریقہ
    firebase_admin.initialize_app(options={'databaseURL': DB_URL})

bot = telebot.TeleBot(BOT_TOKEN)

# --- 3. Smart AI Logic (Direct API - Same as your HTML) ---
def ask_ai_direct(prompt, model_name="gemini-1.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ API Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- 4. Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    # یوزر ٹریکنگ (Firebase)
    try:
        db.reference(f'users/{uid}').update({
            'name': message.from_user.first_name,
            'username': message.from_user.username,
            'last_active': "Now"
        })
    except: pass

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Fast Thinking", "🧠 Pro Thinking", "🔍 AI Search")
    bot.send_message(message.chat.id, "MI AI ACTIVE! 🚀\nHTML Logic Integrated. Poochiye kya poochna hai?", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    text = message.text
    
    # ماڈل کا انتخاب
    selected_model = "gemini-1.5-flash" # Default
    if text == "🧠 Pro Thinking":
        bot.reply_to(message, "Pro Mode (Long Thinking) Active!")
        db.reference(f'users/{uid}').update({'mode': 'gemini-1.5-pro'})
        return
    elif text == "🚀 Fast Thinking":
        bot.reply_to(message, "Fast Mode Active!")
        db.reference(f'users/{uid}').update({'mode': 'gemini-1.5-flash'})
        return

    # ڈیٹا بیس سے موجودہ موڈ نکالنا
    user_mode = db.reference(f'users/{uid}/mode').get() or "gemini-1.5-flash"
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # AI سے جواب لینا (Direct HTML-style Logic)
    result = ask_ai_direct(text, user_mode)
    bot.reply_to(message, result, parse_mode="Markdown")

# --- 5. Start ---
print("MI AI Running with HTML logic...")
bot.infinity_polling()
