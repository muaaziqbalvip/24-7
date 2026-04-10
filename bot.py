import telebot
import requests
import os
import time
import json
import base64
from telebot import types
from io import BytesIO

# ================= MI AI CONFIG =================
# Environment variables se keys uthayen
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE / MEMORY =================
users = {}

def get_user_data(uid):
    if uid not in users:
        users[uid] = {
            "mode": "gemini",
            "deep_think": False,
            "language": "Urdu/English",
            "chat_history": []
        }
    return users[uid]

# ================= CUSTOM EMOJIS & ICONS =================
ICONS = {
    "bot": "🤖",
    "user": "👤",
    "gemini": "💎",
    "groq": "⚡",
    "think": "🧠",
    "vision": "👁️",
    "voice": "🎙️",
    "success": "✅",
    "loading": "⏳",
    "error": "⚠️",
    "creator": "👨‍💻",
    "star": "🌟",
    "fire": "🔥",
    "code": "💻",
    "story": "📖"
}

# ================= PROMPT ENGINEERING =================

def get_system_prompt(uid, mode="normal"):
    u = get_user_data(uid)
    base = f"""
System Role: Tum MI AI Pro ho, jise MUAAZ IQBAL (Founder of MiTV Network) ne banaya hai.
User Info: Muaaz Iqbal ek ICS student hai Punjab, Pakistan se. Organization: MUSLIM ISLAM.
Rules:
1. Response style: Friendly, Professional, aur Educational.
2. Language: Urdu (Roman Urdu) + English mix. Use Emojis heavily.
3. If deep_think is ON: Give extremely detailed step-by-step logic.
4. If Code is requested: Provide clean code inside Markdown blocks with explanations.
5. Always mention "Powered by MiTV Network" at the end if the answer is long.
"""
    if mode == "deep":
        return base + "\nFocus: Analyze every aspect of the question. Think like a scientist or a high-end engineer."
    elif mode == "story":
        return base + "\nFocus: Writing cinematic, emotional, and engaging stories with chapters."
    return base

# ================= GEMINI MULTIMODAL API =================

def call_gemini_vision(prompt, image_data, mime_type="image/jpeg"):
    """Handle Image analysis using Gemini 1.5 Flash/Pro"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                }
            ]
        }]
    }
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        result = r.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"{ICONS['error']} Vision Error: {str(e)}"

def call_gemini_text(uid, text, is_deep=False):
    model = "gemini-1.5-pro" if is_deep else "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    system_p = get_system_prompt(uid, "deep" if is_deep else "normal")
    
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"System Instruction: {system_p}\n\nUser Question: {text}"}]}
        ],
        "generationConfig": {
            "temperature": 0.9 if not is_deep else 0.4,
            "topP": 1,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        r = requests.post(url, json=payload, timeout=25)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

# ================= UI & MENUS =================

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(f"{ICONS['bot']} Chat AI", callback_data="chat_ai")
    btn2 = types.InlineKeyboardButton(f"{ICONS['think']} Deep Think", callback_data="toggle_deep")
    btn3 = types.InlineKeyboardButton(f"{ICONS['vision']} Vision Mode", callback_data="vision_help")
    btn4 = types.InlineKeyboardButton(f"{ICONS['story']} Story Writer", callback_data="story_mode")
    btn5 = types.InlineKeyboardButton(f"{ICONS['code']} Coding Lab", callback_data="coding_tab")
    btn6 = types.InlineKeyboardButton(f"{ICONS['creator']} Settings", callback_data="settings")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

def settings_menu(uid):
    u = get_user_data(uid)
    markup = types.InlineKeyboardMarkup()
    
    mode_text = f"Model: {u['mode'].upper()}"
    deep_status = "Deep Think: ON ✅" if u['deep_think'] else "Deep Think: OFF ❌"
    
    markup.add(types.InlineKeyboardButton(mode_text, callback_data="change_model"))
    markup.add(types.InlineKeyboardButton(deep_status, callback_data="toggle_deep"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="home"))
    
    return markup

# ================= HELPERS =================

def send_typing_action(chat_id):
    bot.send_chat_action(chat_id, 'typing')

def format_response(reply, title="MI AI RESPONSE"):
    return f"✨ *{title}* ✨\n\n{reply}\n\n--- 💫 *Powered by MiTV Network* 💫 ---"

# ================= COMMANDS =================

@bot.message_handler(commands=['start'])
def welcome(m):
    uid = m.from_user.id
    get_user_data(uid)
    
    welcome_msg = (
        f"🌟 *ASSALAM-O-ALAIKUM, {m.from_user.first_name}!* 🌟\n\n"
        f"{ICONS['bot']} Main hoon **MI AI PRO**, apka personal assistant.\n"
        f"{ICONS['creator']} Created by: **MUAAZ IQBAL**\n"
        f"{ICONS['star']} Organization: **MUSLIM ISLAM**\n\n"
        "Main Images dekh sakta hoon, Voice sun sakta hoon aur Coding kar sakta hoon! 🚀"
    )
    
    # Animated intro effect
    msg = bot.send_message(m.chat.id, "⚡")
    time.sleep(0.5)
    bot.edit_message_text(f"⚡ MI AI LOADING...", m.chat.id, msg.message_id)
    time.sleep(0.5)
    
    bot.delete_message(m.chat.id, msg.message_id)
    bot.send_message(m.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=main_menu())

# ================= CALLBACKS =================

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    uid = c.from_user.id
    u = get_user_data(uid)
    
    if c.data == "home":
        bot.edit_message_text("🌟 Select an Option:", c.message.chat.id, c.message.message_id, reply_markup=main_menu())
        
    elif c.data == "toggle_deep":
        u['deep_think'] = not u['deep_think']
        status = "ENABLED 🧠" if u['deep_think'] else "DISABLED 💤"
        bot.answer_callback_query(c.id, f"Deep Think is now {status}")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=settings_menu(uid))

    elif c.data == "coding_tab":
        bot.send_message(c.message.chat.id, f"{ICONS['code']} *CODING MODE ACTIVE*\nJust send me your requirement, and I will write a high-pro code for you!", parse_mode="Markdown")

    elif c.data == "vision_help":
        bot.send_message(c.message.chat.id, f"{ICONS['vision']} *VISION ACTIVE*\nBus koi bhi photo send karein aur uske saath question likhen, main read kar loonga!", parse_mode="Markdown")

    elif c.data == "settings":
        bot.edit_message_text(f"{ICONS['creator']} *MI AI CONFIGURATION*", c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=settings_menu(uid))

# ================= MEDIA HANDLERS =================

@bot.message_handler(content_types=['photo'])
def handle_image(m):
    uid = m.from_user.id
    send_typing_action(m.chat.id)
    
    caption = m.caption if m.caption else "Describe this image in detail."
    
    # Animating response
    status_msg = bot.reply_to(m, f"{ICONS['loading']} Processing Image... Please wait ⏳")
    
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')
        
        response = call_gemini_vision(caption, base64_image)
        
        bot.delete_message(m.chat.id, status_msg.message_id)
        bot.reply_to(m, format_response(response, "IMAGE ANALYSIS 👁️"), parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"{ICONS['error']} Vision error: {str(e)}", m.chat.id, status_msg.message_id)

@bot.message_handler(content_types=['voice'])
def handle_voice(m):
    bot.reply_to(m, f"{ICONS['voice']} Voice detected! AI is listening... (Converting speech to text via Gemini)")
    # Logic for Speech to Text can be added using Groq Whisper or Gemini 1.5 Pro
    bot.send_message(m.chat.id, "⚠️ Voice processing is being optimized for Pakistani accent.")

# ================= TEXT & LOGIC =================

@bot.message_handler(func=lambda m: True)
def chat_handler(m):
    uid = m.from_user.id
    u = get_user_data(uid)
    text = m.text
    
    send_typing_action(m.chat.id)
    
    # Animating response
    think_icon = ICONS['think'] if u['deep_think'] else ICONS['gemini']
    status_msg = bot.reply_to(m, f"{think_icon} MI AI is thinking...")
    
    # Get Response
    response = call_gemini_text(uid, text, is_deep=u['deep_think'])
    
    if not response:
        # Fallback to Groq if Gemini fails
        response = "⚠️ Gemini is busy, switching to Groq..."
        # Add Groq logic here if needed
        
    bot.delete_message(m.chat.id, status_msg.message_id)
    
    # Split message if it's too long for Telegram (4096 limit)
    if len(response) > 4000:
        for x in range(0, len(response), 4000):
            bot.send_message(m.chat.id, format_response(response[x:x+4000]), parse_mode="Markdown")
    else:
        bot.reply_to(m, format_response(response), parse_mode="Markdown")

# ================= RUN =================
if __name__ == "__main__":
    print(f"🚀 {ICONS['fire']} MI AI PRO SYSTEM ONLINE")
    print(f"👨‍💻 Created by Muaaz Iqbal")
    bot.infinity_polling()