import telebot
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from telebot import types
import time

# --- 1. Configurations ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"
DB_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com"

# --- 2. Firebase Connection (No File Required Fix) ---
if not firebase_admin._apps:
    # Firebase کو صرف ڈیٹا بیس یو آر ایل سے انیشیلائز کرنا
    firebase_admin.initialize_app(options={'databaseURL': DB_URL})

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --- 3. Smart AI Logic (Auto-Model Detection) ---
def ask_ai(prompt, mode="fast"):
    # خودکار ماڈل سلیکشن
    if mode == "pro":
        model_name = "gemini-1.5-pro" # بھاری کام کے لیے
    elif mode == "search":
        model_name = "gemini-1.5-flash" # سرچ اور تیز کام کے لیے
        prompt = f"Search and provide detailed info: {prompt}"
    else:
        model_name = "gemini-1.5-flash"

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Yar Maaz, Error aa raha hai: {str(e)}"

# --- 4. User Onboarding (Tracking) ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    user_ref = db.reference(f'users/{uid}')
    
    if not user_ref.get():
        msg = bot.send_message(message.chat.id, "Welcome to **MI AI**! 🚀\n\nRegistration Required.\nPlease enter your **Full Name**:")
        bot.register_next_step_handler(msg, process_name)
    else:
        show_main_menu(message)

def process_name(message):
    uid = str(message.from_user.id)
    db.reference(f'users/{uid}').update({'name': message.text})
    msg = bot.send_message(message.chat.id, "Now send your **Phone Number**:")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    uid = str(message.from_user.id)
    db.reference(f'users/{uid}').update({'phone': message.text})
    msg = bot.send_message(message.chat.id, "Lastly, your **Email Address**:")
    bot.register_next_step_handler(msg, process_email)

def process_email(message):
    uid = str(message.from_user.id)
    db.reference(f'users/{uid}').update({'email': message.text, 'mode': 'fast'})
    bot.send_message(message.chat.id, "✅ Data Saved! You are now tracked.")
    show_main_menu(message)

# --- 5. Navigation & Modes ---
def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🚀 Fast Mode", "🧠 Pro Thinking", "🔍 AI Search", "📊 My Data")
    bot.send_message(message.chat.id, "MI AI ACTIVE. Select Mode:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = str(message.from_user.id)
    text = message.text
    user_ref = db.reference(f'users/{uid}')

    if text == "🚀 Fast Mode":
        user_ref.update({'mode': 'fast'})
        bot.reply_to(message, "Switched to Fast Mode! ⚡")
    elif text == "🧠 Pro Thinking":
        user_ref.update({'mode': 'pro'})
        bot.reply_to(message, "Switched to Pro Thinking (Deep Analysis)! 🧠")
    elif text == "🔍 AI Search":
        user_ref.update({'mode': 'search'})
        bot.reply_to(message, "AI Search Mode Active! 🔍")
    elif text == "📊 My Data":
        data = user_ref.get()
        bot.reply_to(message, f"👤 Name: {data['name']}\n📞 Phone: {data['phone']}\n📧 Email: {data['email']}")
    else:
        mode = user_ref.child('mode').get() or 'fast'
        bot.send_chat_action(message.chat.id, 'typing')
        result = ask_ai(text, mode)
        bot.reply_to(message, result, parse_mode="Markdown")

# --- 6. Stay Alive ---
print("MI AI Running with Auto-Detection...")
bot.infinity_polling()
