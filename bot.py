import telebot
from telebot import types
import requests
import os
import time
import json
import base64
import threading
import urllib.parse
from functools import wraps

# ==============================================================
# 🌟 MI AI PRO ULTIMATE - CREATED BY MUAAZ IQBAL
# 🏢 ORGANIZATION: MUSLIM ISLAM | PROJECT: MiTV Network
# ==============================================================

# Apni API Keys yahan dalein ya Environment Variables se set karein
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE / MEMORY =================
# User ka data save karne ke liye dictionary
users_db = {}

def get_user(uid):
    if uid not in users_db:
        users_db[uid] = {
            "current_ai": "gemini", # Options: gemini, groq, openrouter
            "deep_think": False,
            "mode": "chat", # Options: chat, story, code, search
            "history": []
        }
    return users_db[uid]

# ================= CUSTOM EMOJIS =================
ICONS = {
    "bot": "🤖", "user": "👤", "gemini": "💎", "groq": "⚡", 
    "openrouter": "🌌", "think": "🧠", "vision": "👁️", "search": "🌐",
    "success": "✅", "loading": "⏳", "error": "⚠️", "creator": "👨‍💻", 
    "star": "🌟", "fire": "🔥", "code": "💻", "story": "📖", "settings": "⚙️"
}

# ================= PROMPT ENGINEERING =================

def get_system_prompt(uid):
    u = get_user(uid)
    base = f"""
Tumhara naam MI AI Pro hai. Tumhe MUAAZ IQBAL ne banaya hai.
Muaaz Iqbal MiTV Network ka founder hai aur MUSLIM ISLAM organization chalata hai.
Muaaz ek ICS computer science student hai (Govt Islamia Graduate College, Punjab, Pakistan).
Tumhara tone friendly, respectful, aur highly educational hona chahiye.
Language: Roman Urdu (Hindi/Urdu Latin) aur English mix use karo.
Emojis ka bohot zyada use karo.
Har detail ko explain karo.
"""
    if u['deep_think']:
        base += "\n[DEEP THINK MODE ON]: Har problem ko step-by-step tod kar samjhao. Logic aur reasoning par focus karo. Ek expert teacher ki tarah behave karo."
    
    if u['mode'] == "code":
        base += "\n[CODING MODE ON]: Hamesha clean, well-commented code do. Markdown code blocks use karo."
    elif u['mode'] == "story":
        base += "\n[STORY MODE ON]: Behtareen cinematic aur emotional stories likho chapters ke sath."
    elif u['mode'] == "search":
        base += "\n[SEARCH AI MODE]: Niche diye gaye search results ko analyze karke user ko ek clear, summarize aur accurate answer do."

    return base

# ================= API INTEGRATIONS =================

def call_gemini(uid, prompt, is_vision=False, image_data=None, mime_type="image/jpeg"):
    u = get_user(uid)
    system_p = get_system_prompt(uid)
    
    # Agar Deep Think ON hai toh Gemini Pro use karega, warna Flash
    model_name = "gemini-1.5-pro" if u['deep_think'] else "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    if is_vision and image_data:
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"System: {system_p}\n\nUser: {prompt}"},
                    {"inline_data": {"mime_type": mime_type, "data": image_data}}
                ]
            }]
        }
    else:
        payload = {
            "contents": [{"parts": [{"text": f"System: {system_p}\n\nUser: {prompt}"}]}],
            "generationConfig": {"temperature": 0.3 if u['deep_think'] else 0.8}
        }
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return None

def call_groq(uid, prompt):
    u = get_user(uid)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    model = "llama3-70b-8192" if u['deep_think'] else "llama3-8b-8192"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": get_system_prompt(uid)},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None

def call_openrouter(uid, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": get_system_prompt(uid)},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return None

def web_search_ai(uid, query):
    """DuckDuckGo HTML Scraping for real-time data"""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(search_url, headers=headers, timeout=10)
        
        # Simple text extraction
        text_data = res.text[:3000] # Taking first 3000 chars of HTML as raw context
        
        # Pass to Gemini to format it nicely
        ai_prompt = f"User Query: {query}\n\nSearch Results Raw Data:\n{text_data}\n\nIs data ko read karke user ko ek acha aur accurate jawab do."
        
        # Force Gemini for search parsing
        return call_gemini(uid, ai_prompt)
    except Exception as e:
        return f"⚠️ Search failed: {str(e)}"

# ================= UI / KEYBOARDS =================

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['bot']} AI Chat", callback_data="mode_chat"),
        types.InlineKeyboardButton(f"{ICONS['settings']} Select AI Model", callback_data="ai_list")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['search']} Web Search AI", callback_data="mode_search"),
        types.InlineKeyboardButton(f"{ICONS['think']} Deep Think", callback_data="toggle_deep")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['story']} Story Mode", callback_data="mode_story"),
        types.InlineKeyboardButton(f"{ICONS['code']} Code Lab", callback_data="mode_code")
    )
    return markup

def ai_list_menu(uid):
    u = get_user(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Tick mark the active AI
    g_btn = f"{ICONS['gemini']} Gemini (Google)" + (" ✅" if u['current_ai'] == 'gemini' else "")
    gr_btn = f"{ICONS['groq']} Groq (LLaMA 3)" + (" ✅" if u['current_ai'] == 'groq' else "")
    op_btn = f"{ICONS['openrouter']} OpenRouter (GPT)" + (" ✅" if u['current_ai'] == 'openrouter' else "")
    
    markup.add(
        types.InlineKeyboardButton(g_btn, callback_data="set_ai_gemini"),
        types.InlineKeyboardButton(gr_btn, callback_data="set_ai_groq"),
        types.InlineKeyboardButton(op_btn, callback_data="set_ai_openrouter"),
        types.InlineKeyboardButton("🔙 Back to Home", callback_data="go_home")
    )
    return markup

def format_msg(reply, uid):
    u = get_user(uid)
    ai_used = u['current_ai'].upper()
    deep_str = "🧠 DEEP THINK" if u['deep_think'] else "⚡ FAST MODE"
    return f"**MI AI PRO** | {ai_used} | {deep_str}\n━━━━━━━━━━━━━━━━━━\n\n{reply}\n\n━━━━━━━━━━━━━━━━━━\n👨‍💻 _Powered by MiTV Network_"

# ================= ANIMATIONS =================

def animated_thinking(chat_id, message_id):
    """Animates the bot's 'thinking' message"""
    frames = [
        "⏳ MI AI is thinking.",
        "🧠 MI AI is processing..",
        "⚙️ Analyzing request...",
        "💎 Generating response...."
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id, message_id)
            time.sleep(0.5)
        except:
            pass

# ================= HANDLERS =================

@bot.message_handler(commands=['start', 'help'])
def start_command(m):
    uid = m.from_user.id
    u = get_user(uid)
    
    msg = bot.send_message(m.chat.id, "🚀")
    time.sleep(0.5)
    bot.edit_message_text("🚀 Booting MI AI Pro...", m.chat.id, msg.message_id)
    time.sleep(0.5)
    
    welcome_text = (
        f"🌟 **Assalam-o-Alaikum, {m.from_user.first_name}!** 🌟\n\n"
        f"Main **MI AI Pro** hoon, created by **MUAAZ IQBAL**.\n"
        f"Organization: **MUSLIM ISLAM**\n\n"
        f"Main text, image, coding, aur live internet search sab kar sakta hoon. "
        f"Niche diye gaye menu se apne features select karein:"
    )
    bot.delete_message(m.chat.id, msg.message_id)
    bot.send_message(m.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def callback_manager(c):
    uid = c.from_user.id
    u = get_user(uid)
    data = c.data
    
    # Navigation
    if data == "go_home":
        bot.edit_message_text("🌟 **MI AI PRO - MAIN MENU**", c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=main_menu())
    
    # AI Selection
    elif data == "ai_list":
        bot.edit_message_text("⚙️ **Select your preferred AI Engine:**", c.message.chat.id, c.message.message_id, parse_mode="Markdown", reply_markup=ai_list_menu(uid))
    
    elif data.startswith("set_ai_"):
        new_ai = data.split("_")[2] # gemini, groq, openrouter
        u['current_ai'] = new_ai
        bot.answer_callback_query(c.id, f"✅ Switched to {new_ai.upper()}")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=ai_list_menu(uid))
        
    # Deep Think Toggle
    elif data == "toggle_deep":
        u['deep_think'] = not u['deep_think']
        status = "ON 🧠" if u['deep_think'] else "OFF ⚡"
        bot.answer_callback_query(c.id, f"Deep Think is now {status}")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=main_menu())
        
    # Modes
    elif data.startswith("mode_"):
        new_mode = data.split("_")[1]
        u['mode'] = new_mode
        bot.answer_callback_query(c.id, f"{new_mode.upper()} Mode Activated!")
        
        mode_msgs = {
            "chat": "💬 **Normal Chat Mode ON.** Mujhse kuch bhi puchiye!",
            "search": "🌐 **Web Search AI ON.** Jo topic likhenge, main internet se search karke launga.",
            "story": "📖 **Story Mode ON.** Topic batayein aur main ek emotional kahani likhunga.",
            "code": "💻 **Coding Mode ON.** Apni app ya script ki requirement batayein."
        }
        bot.send_message(c.message.chat.id, mode_msgs[new_mode], parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_vision(m):
    uid = m.from_user.id
    u = get_user(uid)
    
    status_msg = bot.reply_to(m, "👁️ Image received. Animating process...")
    threading.Thread(target=animated_thinking, args=(m.chat.id, status_msg.message_id)).start()
    
    try:
        caption = m.caption if m.caption else "Is image ko detail mein samjhao."
        file_info = bot.get_file(m.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')
        
        # Vision hamesha Gemini se hogi
        response = call_gemini(uid, caption, is_vision=True, image_data=base64_image)
        
        if not response:
            response = "⚠️ Image process nahi ho saki."
            
        bot.delete_message(m.chat.id, status_msg.message_id)
        bot.reply_to(m, format_msg(response, uid), parse_mode="Markdown")
        
    except Exception as e:
        bot.delete_message(m.chat.id, status_msg.message_id)
        bot.reply_to(m, f"Error: {e}")

@bot.message_handler(func=lambda m: True)
def handle_text(m):
    uid = m.from_user.id
    u = get_user(uid)
    text = m.text
    
    # 1. Send initial status
    status_msg = bot.reply_to(m, "🔄 Processing...")
    
    # 2. Run animation in background
    anim_thread = threading.Thread(target=animated_thinking, args=(m.chat.id, status_msg.message_id))
    anim_thread.start()
    
    # 3. Route logic based on Mode & AI
    response = None
    
    if u['mode'] == "search":
        response = web_search_ai(uid, text)
    else:
        # Chat, Code, Story modes
        if u['current_ai'] == "gemini":
            response = call_gemini(uid, text)
        elif u['current_ai'] == "groq":
            response = call_groq(uid, text)
        elif u['current_ai'] == "openrouter":
            response = call_openrouter(uid, text)
            
    # Fallback
    if not response:
        response = "⚠️ API limit reached ya network issue hai. Kripya doosra AI model select karein menu se."
        
    # 4. Wait for animation to finish minimal time then delete
    time.sleep(1.5) 
    bot.delete_message(m.chat.id, status_msg.message_id)
    
    # 5. Send final large text chunking
    final_text = format_msg(response, uid)
    
    if len(final_text) > 4000:
        for x in range(0, len(final_text), 4000):
            bot.send_message(m.chat.id, final_text[x:x+4000], parse_mode="Markdown")
    else:
        bot.reply_to(m, final_text, parse_mode="Markdown")

# ================= SERVER START =================
if __name__ == "__main__":
    print("========================================")
    print("🌟 MI AI PRO ULTIMATE SERVER STARTED 🌟")
    print("👨‍💻 By: Muaaz Iqbal | MUSLIM ISLAM")
    print("========================================")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot crashed: {e}")