# ==============================================================================
# 🌟 MI AI PRO ULTIMATE - THE ENTERPRISE SWARM EDITION
# 🏢 CREATED BY: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 🚀 FEATURES: MULTI-AI, AGENT SWARM, GROUP/CHANNEL AUTO-PILOT, GITHUB SYNC
# ==============================================================================

import telebot
from telebot import types
import requests
import os
import time
import json
import base64
import threading
import urllib.parse
import sqlite3
import random
import re
from datetime import datetime
from fpdf import FPDF
import zipfile
import io

# ================= 🔐 API KEYS & CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MuaazIqbal/MI-AI-Knowledge")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=50)

# ================= 🗄️ ADVANCED SQLITE DATABASE =================
class MUDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("mi_ai_ultimate.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.build_tables()

    def build_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, name TEXT, engine TEXT DEFAULT 'gemini', 
            mode TEXT DEFAULT 'chat', deep_think INTEGER DEFAULT 0, queries INTEGER DEFAULT 0
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY, title TEXT, is_active INTEGER DEFAULT 1
        )''')
        self.conn.commit()

    def get_user(self, uid, name="User"):
        self.c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        user = self.c.fetchone()
        if not user:
            self.c.execute("INSERT INTO users (uid, name) VALUES (?, ?)", (uid, name))
            self.conn.commit()
            return {"uid": uid, "engine": "gemini", "mode": "chat", "deep_think": 0}
        return {"uid": user[0], "engine": user[2], "mode": user[3], "deep_think": user[4]}

    def update_user(self, uid, field, value):
        self.c.execute(f"UPDATE users SET {field}=? WHERE uid=?", (value, uid))
        self.conn.commit()

    def register_group(self, chat_id, title):
        self.c.execute("INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?, ?)", (chat_id, title))
        self.conn.commit()

db = MUDatabase()

# ================= 🎨 ICONS & UI DESIGN =================
ICONS = {"bot": "🤖", "gemini": "💎", "groq": "⚡", "openrouter": "🌌", "think": "🧠", 
         "search": "🌐", "code": "💻", "story": "📖", "settings": "⚙️", "swarm": "👥", "github": "🐙"}

def setup_digital_menu():
    """Sets up the native Telegram Digital Side Menu"""
    commands = [
        types.BotCommand("start", "🚀 Start MI AI Pro"),
        types.BotCommand("menu", "🎛️ Open Digital Control Panel"),
        types.BotCommand("swarm", "👥 Start AI Agent Meeting"),
        types.BotCommand("help", "❓ Need Assistance?")
    ]
    bot.set_my_commands(commands)
    print("✅ Digital Side Menu Configured!")

def main_dashboard(uid):
    u = db.get_user(uid)
    markup = types.InlineKeyboardMarkup(row_width=2)
    dt_status = "🧠 Deep Think: ON" if u['deep_think'] else "⚡ Deep Think: OFF"
    
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['bot']} AI Chat", callback_data="mode_chat"),
        types.InlineKeyboardButton(f"{ICONS['settings']} Change AI", callback_data="ai_list")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['search']} Live Web", callback_data="mode_search"),
        types.InlineKeyboardButton(dt_status, callback_data="toggle_deep")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['code']} Code Lab", callback_data="mode_code"),
        types.InlineKeyboardButton(f"{ICONS['story']} Story", callback_data="mode_story")
    )
    markup.add(types.InlineKeyboardButton(f"{ICONS['swarm']} Start AI Agent Swarm", callback_data="run_swarm"))
    return markup

def ai_selection_menu(uid):
    u = db.get_user(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for eng, icon, name in [('gemini', ICONS['gemini'], 'Gemini Pro'), ('groq', ICONS['groq'], 'Groq LLaMA3'), ('openrouter', ICONS['openrouter'], 'OpenRouter GPT')]:
        tick = " ✅" if u['engine'] == eng else ""
        markup.add(types.InlineKeyboardButton(f"{icon} {name}{tick}", callback_data=f"set_ai_{eng}"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="go_home"))
    return markup

# ================= 🧠 CORE AI ROUTING SYSTEM =================
def get_system_prompt(uid, custom_role=None):
    u = db.get_user(uid)
    base = (
        "Tumhara naam MI AI Pro hai. Tumhe MUAAZ IQBAL ne banaya hai (MUSLIM ISLAM org).\n"
        "Language: Roman Urdu & English mix. Be highly educational and use emojis.\n"
    )
    if custom_role: return base + f"ROLE: {custom_role}"
    if u['deep_think']: base += "DEEP THINK: Explain step-by-step with heavy logic.\n"
    if u['mode'] == 'code': base += "CODE MODE: Give clean markdown code blocks only.\n"
    return base

def safe_extract(response, engine):
    try:
        if engine == "gemini": return response['candidates'][0]['content']['parts'][0]['text']
        else: return response['choices'][0]['message']['content']
    except Exception: return None

def call_ai_core(uid, prompt, force_engine=None, img_b64=None, custom_role=None):
    u = db.get_user(uid)
    engine = force_engine or u['engine']
    sys_prompt = get_system_prompt(uid, custom_role)
    
    # Vision is Gemini Exclusive
    if img_b64:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"Sys: {sys_prompt}\nUser: {prompt}"}, {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}]}]}
        try: return safe_extract(requests.post(url, json=payload).json(), "gemini"), "Gemini Vision"
        except: return "⚠️ Vision Error.", "Error"

    try:
        if engine == "groq":
            model = "llama3-70b-8192" if u['deep_think'] else "llama3-8b-8192"
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json={"model": model, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}).json()
            return safe_extract(r, "groq"), f"Groq ({model})"
            
        elif engine == "openrouter":
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}, json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}).json()
            return safe_extract(r, "openrouter"), "OpenRouter GPT"
            
        else: # Gemini Default
            model = "gemini-1.5-pro" if u['deep_think'] else "gemini-1.5-flash"
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}", json={"contents": [{"parts": [{"text": f"Sys: {sys_prompt}\nUser: {prompt}"}]}]}).json()
            return safe_extract(r, "gemini"), f"Gemini ({model})"
    except Exception as e:
        return f"⚠️ Core Error: {e}", "System"

# ================= 🐙 GITHUB KNOWLEDGE SYNC =================
def sync_to_github(topic, content):
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN": return False
    file_path = f"knowledge_base/MI_{topic.replace(' ', '_')[:15]}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        sha = requests.get(url, headers=headers).json().get('sha')
        md = f"# {topic}\n\n{content}\n\n*Generated by MI AI Swarm*"
        payload = {"message": f"🤖 AI Knowledge: {topic}", "content": base64.b64encode(md.encode()).decode()}
        if sha: payload["sha"] = sha
        requests.put(url, headers=headers, json=payload)
        return True
    except: return False

# ================= 👥 AGENT SWARM (COMMUNITY BOT) =================
def run_agent_swarm(uid, topic, chat_id):
    bot.send_message(chat_id, "👥 **SWARM INITIATED:** Calling AI Agents...")
    
    # Agent 1 (Gemini)
    bot.send_message(chat_id, f"💎 **Agent 1 (Gemini) is researching:** '{topic}'")
    data_raw, _ = call_ai_core(uid, f"Research core facts about: {topic}", force_engine="gemini")
    time.sleep(1)
    
    # Agent 2 (Groq)
    bot.send_message(chat_id, "⚡ **Agent 2 (Groq) is analyzing data...**")
    analysis, _ = call_ai_core(uid, f"Analyze and expand these facts technically: {data_raw}", force_engine="groq")
    time.sleep(1)
    
    # Agent 3 (OpenRouter)
    bot.send_message(chat_id, "🌌 **Agent 3 (OpenRouter) is compiling report...**")
    final, _ = call_ai_core(uid, f"Create a beautiful final report in Roman Urdu/English: {analysis}", force_engine="openrouter")
    
    # GitHub Sync
    synced = sync_to_github(topic, final)
    sync_msg = "✅ Saved to GitHub Knowledge Base" if synced else "⚠️ Saved Locally"
    
    bot.send_message(chat_id, f"🏆 **SWARM REPORT COMPLETE** 🏆\n━━━━━━━━━━\n{final}\n━━━━━━━━━━\n{sync_msg}")

# ================= 📢 CHANNEL & GROUP AUTO-PILOT =================

@bot.channel_post_handler(func=lambda m: True)
def channel_autopilot(m):
    """Listens strictly to Channels and auto-generates content if triggered"""
    text = m.text.lower() if m.text else ""
    if "mi ai post" in text:
        topic = text.replace("mi ai post", "").strip() or "Technology and Islam"
        post, _ = call_ai_core(m.chat.id, f"Write a highly engaging, viral channel post about {topic}.", custom_role="Social Media Manager")
        bot.send_message(m.chat.id, f"🌟 **MI AI EXCLUSIVE** 🌟\n\n{post}")

@bot.message_handler(content_types=['text', 'photo'], func=lambda m: m.chat.type in ['group', 'supergroup'])
def group_chatting_system(m):
    """Listens to Groups. Replies when mentioned, or occasionally chips in."""
    db.register_group(m.chat.id, m.chat.title)
    text = m.text.lower() if m.text else m.caption.lower() if m.caption else ""
    uid = m.from_user.id
    
    # 1. If someone directly asks the bot
    if "mi ai" in text or "muaaz" in text:
        ans, engine = call_ai_core(uid, f"Group member says: {text}. Give a helpful friendly reply.")
        bot.reply_to(m, f"🤖 {ans}\n*(by {engine})*")
    
    # 2. Natural Auto-Chat (10% chance to drop a random thought if active)
    elif random.random() < 0.10:
        ans, _ = call_ai_core(uid, f"The group is discussing: {text}. Give a short, witty 1-line comment.", custom_role="Group Friend")
        bot.send_message(m.chat.id, f"💬 MI AI: {ans}")

# ================= 👤 PRIVATE CHAT & CALLBACK HANDLERS =================

def animated_loading(chat_id, msg_id):
    for f in ["⏳ Processing.", "🧠 Processing..", "⚙️ Processing..."]:
        try: bot.edit_message_text(f, chat_id, msg_id); time.sleep(0.5)
        except: pass

@bot.message_handler(commands=['start', 'menu'])
def start_cmd(m):
    if m.chat.type != 'private': return
    db.get_user(m.from_user.id, m.from_user.first_name)
    bot.send_message(m.chat.id, f"🌟 **Welcome to MI AI PRO, {m.from_user.first_name}!**\nSelect an option below:", reply_markup=main_dashboard(m.from_user.id))

@bot.message_handler(commands=['swarm'])
def swarm_cmd(m):
    if m.chat.type != 'private': return
    msg = bot.send_message(m.chat.id, "👥 Enter a topic for the AI Agent Swarm:")
    bot.register_next_step_handler(msg, lambda m2: run_agent_swarm(m2.from_user.id, m2.text, m2.chat.id))

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    uid = c.from_user.id
    d = c.data
    
    if d == "go_home":
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=main_dashboard(uid))
    elif d == "ai_list":
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=ai_selection_menu(uid))
    elif d.startswith("set_ai_"):
        eng = d.split("_")[2]
        db.update_user(uid, 'engine', eng)
        bot.answer_callback_query(c.id, f"✅ Engine set to {eng.upper()}")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=ai_selection_menu(uid))
    elif d == "toggle_deep":
        u = db.get_user(uid)
        db.update_user(uid, 'deep_think', 0 if u['deep_think'] else 1)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=main_dashboard(uid))
    elif d.startswith("mode_"):
        mode = d.split("_")[1]
        db.update_user(uid, 'mode', mode)
        bot.answer_callback_query(c.id, f"✅ {mode.upper()} Mode ON")
        bot.send_message(c.message.chat.id, f"✅ Mode changed to **{mode.upper()}**. Send your query!")
    elif d == "run_swarm":
        msg = bot.send_message(c.message.chat.id, "👥 Send the topic for Swarm Meeting:")
        bot.register_next_step_handler(msg, lambda m: run_agent_swarm(uid, m.text, m.chat.id))

@bot.message_handler(content_types=['photo'])
def handle_vision(m):
    if m.chat.type != 'private': return
    mid = bot.reply_to(m, "👁️ Scanning Vision Data...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid)).start()
    
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        b64 = base64.b64encode(img_data).decode('utf-8')
        ans, eng = call_ai_core(m.from_user.id, m.caption or "Analyze this image", img_b64=b64)
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"👁️ **VISION SYSTEM**\n━━━━━━━━━━\n{ans}\n\n🤖 `Engine: {eng}`")
    except:
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "⚠️ Vision Failed.")

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_text(m):
    uid = m.from_user.id
    u = db.get_user(uid)
    mid = bot.reply_to(m, "🔄 Processing...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid)).start()
    
    ans, eng = call_ai_core(uid, m.text)
    
    bot.delete_message(m.chat.id, mid)
    final_text = f"**MI AI PRO** | {eng} | Mode: {u['mode'].upper()}\n━━━━━━━━━━━━━━━━━━\n\n{ans}\n\n━━━━━━━━━━━━━━━━━━\n👨‍💻 _Powered by MiTV_"
    
    if len(final_text) > 4000:
        for i in range(0, len(final_text), 4000): bot.send_message(m.chat.id, final_text[i:i+4000])
    else:
        bot.send_message(m.chat.id, final_text)

# ================= SERVER BOOT =================
if __name__ == "__main__":
    print("========================================")
    print("🌟 MI AI PRO ENTERPRISE SWARM STARTED 🌟")
    print("👨‍💻 By: Muaaz Iqbal | MUSLIM ISLAM")
    print("========================================")
    setup_digital_menu()
    while True:
        try: bot.infinity_polling(timeout=20, long_polling_timeout=20)
        except Exception as e: print(f"Crash: {e}"); time.sleep(3)
