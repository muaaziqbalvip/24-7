import telebot
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from telebot import types
import time
import os

# --- Configurations ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"

# Firebase Setup
firebase_config = {
    "apiKey": "AIzaSyBbnU8DkthpYQMHOLLyj6M0cc05qXfjMcw",
    "authDomain": "ramadan-2385b.firebaseapp.com",
    "databaseURL": "https://ramadan-2385b-default-rtdb.firebaseio.com",
    "projectId": "ramadan-2385b",
}

# Initialize Firebase (Using a simple check to avoid re-initialization)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config) # Note: In production use a serviceAccountKey.json
    firebase_admin.initialize_app(cred, {'databaseURL': firebase_config['databaseURL']})

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --- AI Logic ---
def ask_gemini(prompt, model_name="gemini-1.5-flash"):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text

# --- Welcome & Data Collection ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    ref = db.reference(f'users/{user_id}')
    user_data = ref.get()

    if not user_data:
        msg = bot.send_message(message.chat.id, "Welcome to MI AI! 🚀\nPlease enter your **Full Name** to register:")
        bot.register_next_step_handler(msg, save_name)
    else:
        show_menu(message)

def save_name(message):
    user_id = str(message.from_user.id)
    db.reference(f'users/{user_id}').update({'name': message.text})
    msg = bot.send_message(message.chat.id, "Great! Now share your **Phone Number**:")
    bot.register_next_step_handler(msg, save_phone)

def save_phone(message):
    user_id = str(message.from_user.id)
    db.reference(f'users/{user_id}').update({'phone': message.text})
    msg = bot.send_message(message.chat.id, "Lastly, enter your **Email Address**:")
    bot.register_next_step_handler(msg, save_email)

def save_email(message):
    user_id = str(message.from_user.id)
    db.reference(f'users/{user_id}').update({'email': message.text})
    bot.send_message(message.chat.id, "✅ Registration Complete!")
    show_menu(message)

# --- Main Menu ---
def show_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Fast Thinking")
    btn2 = types.KeyboardButton("🧠 Pro Thinking (Long)")
    btn3 = types.KeyboardButton("🔍 Google Search AI")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "MI AI Terminal Active. Select your mode:", reply_markup=markup)

# --- Handling Messages ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = str(message.from_user.id)
    text = message.text

    if text == "🚀 Fast Thinking":
        bot.reply_to(message, "Mode switched to **Fast Thinking**. Send your query!")
        db.reference(f'users/{user_id}').update({'mode': 'fast'})
    elif text == "🧠 Pro Thinking (Long)":
        bot.reply_to(message, "Mode switched to **Pro Thinking**. Deep analysis enabled!")
        db.reference(f'users/{user_id}').update({'mode': 'pro'})
    elif text == "🔍 Google Search AI":
        bot.reply_to(message, "Search Mode enabled. I will search the web for you!")
        db.reference(f'users/{user_id}').update({'mode': 'search'})
    else:
        # Process AI Response based on Mode
        user_mode = db.reference(f'users/{user_id}/mode').get() or 'fast'
        bot.send_chat_action(message.chat.id, 'typing')
        
        if user_mode == 'pro':
            response = ask_gemini(f"Deep Analysis required: {text}", "gemini-1.5-pro")
        else:
            response = ask_gemini(text, "gemini-1.5-flash")
        
        bot.reply_to(message, f"**MI AI Result:**\n\n{response}", parse_mode="Markdown")

# --- Auto Restart Logic (Simulated for GitHub) ---
print("MI AI is Running...")
bot.infinity_polling()
