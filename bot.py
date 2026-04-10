import telebot
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from telebot import types
import traceback

# --- Config ---
BOT_TOKEN = "7942368781:AAGFDlmnBKVKulMR3AHDxLXIgHOgCXjB_Jc"
GEMINI_API_KEY = "AIzaSyDswodCTMu6EpQLcM6BQhv83La0Zunh94I"
DB_URL = "https://ramadan-2385b-default-rtdb.firebaseio.com"

# --- Firebase Fix ---
try:
    if not firebase_admin._apps:
        # بغیر سرٹیفکیٹ فائل کے کنکشن کی کوشش
        firebase_admin.initialize_app(options={'databaseURL': DB_URL})
    print("Firebase Connected Successfully!")
except Exception as e:
    print(f"Firebase Error: {e}")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --- AI Logic ---
def ask_ai(prompt, mode="fast"):
    try:
        model_name = "gemini-1.5-pro" if mode == "pro" else "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# --- Error Handler ---
def report_error(message, error_text):
    full_error = f"⚠️ **System Error Occurred!**\n\n`{error_text}`"
    bot.send_message(message.chat.id, full_error, parse_mode="Markdown")

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start(message):
    try:
        uid = str(message.from_user.id)
        user_ref = db.reference(f'users/{uid}')
        
        # ٹیسٹنگ کے لیے ڈائریکٹ مینو دکھا رہے ہیں اگر رجسٹریشن کا مسئلہ ہو
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add("🚀 Fast Mode", "🧠 Pro Thinking", "🔍 AI Search")
        bot.send_message(message.chat.id, "MI AI ACTIVE! 🚀\nMain online hoon. Kuch bhi poochiye.", reply_markup=markup)
        
        # ڈیٹا محفوظ کرنے کی کوشش
        user_ref.update({'last_seen': time.time()})
    except Exception as e:
        report_error(message, str(e))

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    try:
        text = message.text
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Simple Response Logic
        if "Mode" in text:
            bot.reply_to(message, f"✅ {text} Active!")
        else:
            result = ask_ai(text)
            bot.reply_to(message, result)
            
    except Exception as e:
        # اگر کوڈ کہیں بھی پھنسے گا تو آپ کو ٹیلیگرام پر میسج آئے گا
        error_trace = traceback.format_exc()
        report_error(message, error_trace)

# --- Start ---
print("MI AI is starting...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
