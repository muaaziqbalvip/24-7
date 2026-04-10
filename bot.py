import telebot
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
import time
import os

# --- INITIALIZATION ---
# GitHub Secrets se values uthayega
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Firebase setup
firebase_creds = {
    "apiKey": "AIzaSyBbnU8DkthpYQMHOLLyj6M0cc05qXfjMcw",
    "authDomain": "ramadan-2385b.firebaseapp.com",
    "databaseURL": "https://ramadan-2385b-default-rtdb.firebaseio.com",
    "projectId": "ramadan-2385b",
    "storageBucket": "ramadan-2385b.firebasestorage.app",
}

# Firebase Admin SDK initialization
# Note: Ensure you have your service account json or use databaseURL with public access for testing
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccount.json") # File lazmi honi chahiye
    firebase_admin.initialize_app(cred, {'databaseURL': firebase_config["databaseURL"]})

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

SYSTEM_INSTRUCTION = """
Your name is Muslim Islam AI.
Founder: Muaaz Iqbal (MiTV Network).
Role: Expert Coder, Fast Thinker, Pro Assistant.
Personality: Professional, Magic, and ultra-fast.
You must remember that you are serving under the organization 'MUSLIM ISLAM'.
"""

# --- DATABASE FUNCTIONS ---
def save_user_data(user):
    ref = db.reference(f'Users/{user.id}')
    ref.update({
        'name': f"{user.first_name} {user.last_name or ''}",
        'username': user.username,
        'last_seen': time.ctime()
    })

def log_message(user_id, text):
    ref = db.reference(f'ChatLogs/{user_id}')
    ref.push({
        'time': time.ctime(),
        'msg': text
    })

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    save_user_data(message.from_user)
    msg = "Assalam-o-Alaikum! Main **Muslim Islam AI** hoon.\n\nMuaaz Iqbal ka banaya hua aik fast AI system. Main aapki coding aur research mein madad kar sakta hoon."
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_ai(message):
    try:
        # User details note karna
        save_user_data(message.from_user)
        log_message(message.from_user.id, message.text)
        
        # AI Processing
        prompt = f"{SYSTEM_INSTRUCTION}\nUser {message.from_user.first_name}: {message.text}"
        response = model.generate_content(prompt)
        
        bot.reply_to(message, response.text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "System Busy! Dobara koshish karein.")

# --- AUTO RESTART LOGIC (Internal) ---
print("Muslim Islam AI is active...")
bot.infinity_polling()
