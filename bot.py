import telebot
import requests
import json
from telebot import types

# --- 1. Configurations ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"
DB_BASE_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com/users"

bot = telebot.TeleBot(BOT_TOKEN)

# --- 2. Firebase REST Functions ---
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

# --- 3. Smart AI Routing (HTML Logic) & Memory ---
def ask_ai_smart(chat_history, mode="fast"):
    # آپ کے HTML والے ماڈلز کا Array
    if mode == "pro":
        models = ["gemini-1.5-pro", "gemini-1.5-pro-latest"]
    else:
        models = [
            "gemini-1.5-flash", 
            "gemini-3.1-flash-lite-preview", 
            "gemini-2.0-flash-001"
        ]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # پوری چیٹ ہسٹری بھیج رہے ہیں تاکہ اسے سب یاد رہے
        payload = {"contents": chat_history}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                reply_text = data['candidates'][0]['content']['parts'][0]['text']
                return reply_text, model # کامیابی کی صورت میں جواب اور ماڈل کا نام واپس کریں
            else:
                print(f"{model} Failed or Busy. Trying next...")
                continue # اگر 503 یا کوئی اور ایرر ہو تو اگلا ماڈل ٹرائی کرے گا
        except Exception as e:
            print(f"Network error on {model}: {e}")
            continue

    return "Yar Maaz, sare models busy hain. Try again.", "None"

# --- 4. Bot Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    name = message.from_user.first_name
    
    # یوزر کا بنیادی ڈیٹا اور خالی ہسٹری سیٹ کرنا
    update_user_data(uid, {
        "name": name,
        "username": message.from_user.username,
        "mode": "fast",
        "history": [] # یہ اس کی یادداشت ہے
    })

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Fast Mode", "🧠 Pro Thinking", "🧹 Clear Memory")
    
    welcome_text = f"Assalam-o-Alaikum {name}!\nMain **MI AI** ہوں. میرا سرور روٹنگ لاجک ایکٹو ہے۔\nپوچھیے کیا پوچھنا ہے؟"
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    text = message.text
    
    # موڈ کنٹرولز
    if text == "🚀 Fast Mode":
        update_user_data(uid, {"mode": "fast"})
        bot.reply_to(message, "⚡ **Fast Mode** Active!")
        return
    elif text == "🧠 Pro Thinking":
        update_user_data(uid, {"mode": "pro"})
        bot.reply_to(message, "🧠 **Pro Thinking** Active!")
        return
    elif text == "🧹 Clear Memory":
        update_user_data(uid, {"history": []})
        bot.reply_to(message, "🧹 پچھلی تمام یادداشت ڈیلیٹ کر دی گئی ہے. اب ہم نئی بات شروع کر سکتے ہیں!")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    # 1. یوزر کی پرانی ہسٹری فائر بیس سے نکالیں
    user_data = get_user_data(uid)
    mode = user_data.get("mode", "fast")
    history = user_data.get("history", [])
    
    if not isinstance(history, list):
        history = []

    # 2. یوزر کا نیا میسج ہسٹری میں شامل کریں
    history.append({"role": "user", "parts": [{"text": text}]})

    # 3. AI سے جواب لائیں (Routing لاجک کے ساتھ)
    reply, used_model = ask_ai_smart(history, mode)

    # 4. AI کا جواب بھی ہسٹری میں محفوظ کریں (تاکہ اگلی بار یاد رہے)
    if used_model != "None":
        history.append({"role": "model", "parts": [{"text": reply}]})
        
        # میموری کو لمٹ میں رکھیں (آخری 10 میسجز) تاکہ API کریش نہ ہو
        if len(history) > 10:
            history = history[-10:]
            
        update_user_data(uid, {"history": history})

    # 5. یوزر کو میسج بھیجیں (ساتھ میں نوڈ/ماڈل کا نام بھی)
    final_response = f"{reply}\n\n`[Node: {used_model}]`"
    bot.reply_to(message, final_response, parse_mode="Markdown")

# --- 5. Start Polling ---
print("MI AI Running with Smart Routing & Memory...")
bot.infinity_polling()
