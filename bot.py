# ==============================================================================
# 👑 MI AI PRO ULTIMATE - THE TITAN V15.0 (ENTERPRISE EDITION)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 🏢 PROJECT: MiTV Network | CORE: MULTI-AGENT SWARM SYSTEM
# 📜 LICENSE: FULL BACKEND RIGHTS RESERVED
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
import logging
import random
import re
import io
import zipfile
from datetime import datetime
from fpdf import FPDF
from duckduckgo_search import DDGS

# ================= 🛡️ SYSTEM LOGGING & SECURITY =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MI_TITAN - [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("mi_titan_v15.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 🔐 API CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MuaazIqbal/MI-AI-Knowledge")

# Initialize Bot with High Performance Threading
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=100)

# ================= 🗄️ MEGA SQLITE DATABASE ARCHITECT =================
class MITitanDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("mi_ai_titan_v15.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        # Users Master Table
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, name TEXT, username TEXT, 
            engine TEXT DEFAULT 'gemini', mode TEXT DEFAULT 'chat', 
            deep_think INTEGER DEFAULT 0, total_queries INTEGER DEFAULT 0,
            joined_at TEXT, is_banned INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0
        )''')
        # Group/Channel Intelligence Table
        self.c.execute('''CREATE TABLE IF NOT EXISTS ecosystem (
            chat_id INTEGER PRIMARY KEY, type TEXT, title TEXT, 
            auto_reply INTEGER DEFAULT 1, context_memory TEXT
        )''')
        # Knowledge Base Log
        self.c.execute('''CREATE TABLE IF NOT EXISTS knowledge_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, 
            summary TEXT, file_url TEXT, timestamp TEXT
        )''')
        self.conn.commit()
        logger.info("Titan Database Tables Initialized.")

    # --- User Logic ---
    def sync_user(self, uid, name, username):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("SELECT uid FROM users WHERE uid=?", (uid,))
        if not self.c.fetchone():
            self.c.execute('''INSERT INTO users (uid, name, username, joined_at) 
                             VALUES (?, ?, ?, ?)''', (uid, name, username, date_now))
            self.conn.commit()

    def get_user_config(self, uid):
        self.c.execute("SELECT engine, mode, deep_think, is_admin FROM users WHERE uid=?", (uid,))
        res = self.c.fetchone()
        if res:
            return {"engine": res[0], "mode": res[1], "deep_think": res[2], "is_admin": res[3]}
        return {"engine": "gemini", "mode": "chat", "deep_think": 0, "is_admin": 0}

    def update_config(self, uid, key, value):
        self.c.execute(f"UPDATE users SET {key}=? WHERE uid=?", (value, uid))
        self.conn.commit()

    def increment_query(self, uid):
        self.c.execute("UPDATE users SET total_queries = total_queries + 1 WHERE uid=?", (uid,))
        self.conn.commit()

    # --- Ecosystem Logic ---
    def register_chat(self, chat_id, chat_type, title):
        self.c.execute("INSERT OR IGNORE INTO ecosystem (chat_id, type, title) VALUES (?, ?, ?)", 
                       (chat_id, chat_type, title))
        self.conn.commit()

db = MITitanDatabase()

# ================= 🎨 DIGITAL UI & ASSETS =================
ICONS = {
    "gemini": "💎", "groq": "⚡", "openrouter": "🌌", "think": "🧠",
    "search": "🌐", "code": "💻", "story": "📖", "swarm": "👥",
    "pdf": "📕", "zip": "📦", "admin": "👑", "github": "🐙",
    "success": "✅", "error": "⚠️", "loading": "⏳", "bot": "🤖"
}

def setup_digital_side_menu():
    """Configures the native side-menu in Telegram."""
    try:
        commands = [
            types.BotCommand("start", "🚀 Boot System"),
            types.BotCommand("menu", "🎛️ Control Panel"),
            types.BotCommand("swarm", "👥 Multi-AI Meeting"),
            types.BotCommand("search", "🌐 Internet Search"),
            types.BotCommand("profile", "📊 Usage Stats"),
            types.BotCommand("broadcast", "👑 Admin Broadcast")
        ]
        bot.set_my_commands(commands)
        logger.info("Digital Side Menu Injected Successfully.")
    except Exception as e:
        logger.error(f"Menu Setup Failed: {e}")

def get_main_keyboard(uid):
    u = db.get_user_config(uid)
    markup = types.InlineKeyboardMarkup(row_width=2)
    dt_icon = ICONS['success'] if u['deep_think'] else "⚪"
    
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['bot']} AI Chat", callback_data="set_mode_chat"),
        types.InlineKeyboardButton(f"{ICONS['think']} Deep Think {dt_icon}", callback_data="toggle_deep")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['search']} Web Search", callback_data="set_mode_search"),
        types.InlineKeyboardButton(f"{ICONS['swarm']} AI Swarm", callback_data="trigger_swarm")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['code']} Code Lab", callback_data="set_mode_code"),
        types.InlineKeyboardButton(f"{ICONS['story']} Story Mode", callback_data="set_mode_story")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['pdf']} PDF Creator", callback_data="tool_pdf"),
        types.InlineKeyboardButton(f"{ICONS['zip']} ZIP Project", callback_data="tool_zip")
    )
    markup.add(types.InlineKeyboardButton(f"{ICONS['gemini']} Select AI Engine", callback_data="menu_engines"))
    return markup

def get_engine_keyboard(uid):
    u = db.get_user_config(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    engines = [
        ('gemini', f"{ICONS['gemini']} Google Gemini Pro"),
        ('groq', f"{ICONS['groq']} Groq LLaMA 3.3"),
        ('openrouter', f"{ICONS['openrouter']} OpenRouter GPT-4")
    ]
    for key, label in engines:
        tick = " ✅" if u['engine'] == key else ""
        markup.add(types.InlineKeyboardButton(f"{label}{tick}", callback_data=f"set_eng_{key}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="go_home"))
    return markup

# ================= 🧠 QUANTUM AI BRAIN (MULTI-NODE ROUTER) =================
def build_system_prompt(uid, role_override=None):
    u = db.get_user_config(uid)
    base = (
        "Tumhara naam MI AI Pro Ultimate hai. Tumhe MUAAZ IQBAL ne banaya hai.\n"
        "Muaaz Iqbal MUSLIM ISLAM organization ka founder hai aur MiTV Network chalata hai.\n"
        "Tum ek highly advanced, polite aur intellectual AI ho.\n"
        "Language: Roman Urdu aur English ka behtareen mix use karo.\n"
        "Har baat ko detail se samjhao aur emojis ka bharpoor use karo.\n"
    )
    if role_override: return base + f"CURRENT ROLE: {role_override}"
    if u['deep_think']: base += "[DEEP THINK]: Logic aur reasoning par focus karo, step-by-step samjhao.\n"
    if u['mode'] == 'code': base += "[CODE MODE]: Clean code, comments aur optimizations provide karo.\n"
    return base

def call_ai_titan(uid, prompt, engine_override=None, image_b64=None, role=None):
    """
    Main Neural Router with Automatic Fallback.
    If Node A fails, Node B takes over automatically.
    """
    db.increment_query(uid)
    u = db.get_user_config(uid)
    engine = engine_override or u['engine']
    sys_prompt = build_system_prompt(uid, role)
    
    # --- 👁️ VISION HANDLER ---
    if image_b64:
        # Vision always uses Gemini Pro
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"Sys: {sys_prompt}\nUser: {prompt}"}, {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}]}]}
        try:
            r = requests.post(url, json=payload, timeout=30).json()
            return r['candidates'][0]['content']['parts'][0]['text'], "Gemini Vision 👁️"
        except: return "⚠️ Vision node failed.", "Error"

    # --- 📝 TEXT HANDLER (WITH FALLBACKS) ---
    response_text = None
    node_used = "None"

    # Step 1: Try Selected Engine
    try:
        if engine == "groq":
            model = "llama-3.3-70b-versatile" if u['deep_think'] else "llama3-8b-8192"
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                             headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                             json={"model": model, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}).json()
            response_text = r['choices'][0]['message']['content']
            node_used = f"Groq ({model}) ⚡"
        elif engine == "openrouter":
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                             json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}).json()
            response_text = r['choices'][0]['message']['content']
            node_used = "OpenRouter 🌌"
    except Exception as e:
        logger.error(f"Primary Node {engine} failed: {e}")

    # Step 2: Fallback to Gemini if Step 1 failed
    if not response_text:
        try:
            model = "gemini-1.5-pro" if u['deep_think'] else "gemini-1.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            r = requests.post(url, json={"contents": [{"parts": [{"text": f"Sys: {sys_prompt}\nUser: {prompt}"}]}]}).json()
            response_text = r['candidates'][0]['content']['parts'][0]['text']
            node_used = f"Gemini ({model}) 💎"
        except Exception as e:
            return f"⚠️ All Neural Nodes are Jammed: {e}", "System Failure"

    return response_text, node_used

# ================= 👥 AGENT SWARM PROTOCOL (COMMUNITY) =================
def run_swarm_protocol(uid, topic, chat_id):
    """Multiple AI models having a meeting on a topic."""
    status_msg = bot.send_message(chat_id, f"{ICONS['swarm']} **Swarm Meeting Started: '{topic}'**")
    
    # Node 1: Researcher (Gemini)
    bot.edit_message_text(f"{ICONS['gemini']} Agent 1 (Gemini) is researching...", chat_id, status_msg.message_id)
    research, _ = call_ai_titan(uid, f"Research core facts: {topic}", engine_override="gemini", role="Researcher")
    
    # Node 2: Logic Expander (Groq)
    bot.edit_message_text(f"{ICONS['groq']} Agent 2 (Groq) is expanding logic...", chat_id, status_msg.message_id)
    logic, _ = call_ai_titan(uid, f"Deeply analyze and expand this research:\n{research}", engine_override="groq", role="Analyst")
    
    # Node 3: Formatter (OpenRouter)
    bot.edit_message_text(f"{ICONS['openrouter']} Agent 3 (OpenRouter) is finalizing report...", chat_id, status_msg.message_id)
    final_report, _ = call_ai_titan(uid, f"Take this analysis and create a professional Roman Urdu guide:\n{logic}", engine_override="openrouter", role="Technical Writer")
    
    # GitHub Sync
    bot.edit_message_text(f"{ICONS['github']} Syncing to GitHub Knowledge Base...", chat_id, status_msg.message_id)
    sync_success = sync_knowledge_github(topic, final_report)
    sync_status = "✅ Synced to GitHub" if sync_success else "⚠️ GitHub Token Missing"
    
    bot.delete_message(chat_id, status_msg.message_id)
    
    output = (
        f"👥 **MI AI SWARM INTELLIGENCE REPORT** 👥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Topic:** {topic}\n"
        f"**Status:** {sync_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{final_report}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 *Created by Muaaz Iqbal's Multi-Agent System*"
    )
    
    if len(output) > 4000:
        for x in range(0, len(output), 4000): bot.send_message(chat_id, output[x:x+4000])
    else: bot.send_message(chat_id, output, parse_mode="Markdown")

def sync_knowledge_github(topic, content):
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN": return False
    safe_topic = re.sub(r'\W+', '_', topic.lower()[:20])
    path = f"knowledge_logs/MI_TITAN_{safe_topic}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        md_content = f"# MI AI Knowledge Base: {topic}\n\n**Date:** {datetime.now()}\n\n{content}"
        b64 = base64.b64encode(md_content.encode()).decode()
        payload = {"message": f"🤖 Knowledge Sync: {topic}", "content": b64}
        if sha: payload["sha"] = sha
        r = requests.put(url, headers=headers, json=payload)
        return r.status_code in [200, 201]
    except: return False

# ================= 🌐 LIVE WEB SEARCH (DUCKDUCKGO) =================
def live_web_search(uid, query):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        
        context = ""
        for r in results: context += f"Title: {r['title']}\nSnippet: {r['body']}\n\n"
        
        prompt = f"Query: {query}\n\nInternet Data:\n{context}\n\nSummarize this into a perfect report."
        ans, node = call_ai_titan(uid, prompt, role="Internet Researcher")
        return f"🌐 **LIVE INTERNET SEARCH**\n━━━━━━━━━━━━━━━━━━━━━━\n{ans}\n\n`Source: DDG | Node: {node}`"
    except Exception as e:
        return f"⚠️ Search Error: {str(e)}"

# ================= 🎨 PDF & ZIP ARCHITECTS =================
def generate_pdf_document(uid, topic):
    content, _ = call_ai_titan(uid, f"Write a 5-page book on: {topic}. Plain text only.", role="Author")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"MI AI TITAN - KNOWLEDGE REPORT", 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def generate_zip_project(uid, prompt):
    structure_prompt = "Generate a full coding project. Format: <<<FILE: name>>> code <<<ENDFILE>>>"
    code_raw, _ = call_ai_titan(uid, prompt, role=structure_prompt)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        files = re.findall(r'<<<FILE:\s*(.+?)>>>(.*?)(?:<<<ENDFILE>>>|\Z)', code_raw, re.DOTALL)
        if files:
            for name, code in files: z.writestr(name.strip(), code.strip())
        else: z.writestr("project_logic.py", code_raw)
        z.writestr("README.md", f"# MI Project\nGenerated for: {prompt}")
    buf.seek(0)
    return buf

# ================= 🚀 TELEGRAM BOT HANDLERS =================

@bot.message_handler(commands=['start', 'menu'])
def welcome(m):
    uid = m.from_user.id
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    
    if m.chat.type == 'private':
        welcome_msg = (
            f"🌟 **AS-SALAM-O-ALAIKUM!** 🌟\n\n"
            f"Main **MI AI PRO TITAN V15** hoon. Muaaz Iqbal ka banaya gaya sabse powerful AI.\n\n"
            f"Main Groups aur Channels mein **Har Message** ka jawab de sakta hoon. "
            f"Niche diye gaye Digital Menu se system control karein."
        )
        bot.send_message(m.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=get_main_keyboard(uid))
    else:
        db.register_chat(m.chat.id, m.chat.type, m.chat.title)
        bot.send_message(m.chat.id, "🤖 **MI AI TITAN ACTIVATED IN THIS GROUP!**\nMain ab har message ko monitor karunga.")

@bot.message_handler(commands=['swarm'])
def cmd_swarm(m):
    msg = bot.send_message(m.chat.id, "👥 Enter topic for Swarm Intelligence Meeting:")
    bot.register_next_step_handler(msg, lambda m2: run_swarm_protocol(m2.from_user.id, m2.text, m2.chat.id))

@bot.callback_query_handler(func=lambda c: True)
def process_callbacks(c):
    uid = c.from_user.id
    d = c.data
    
    if d == "go_home":
        bot.edit_message_text("🎛️ **MI TITAN CONTROL PANEL**", c.message.chat.id, c.message.message_id, reply_markup=get_main_keyboard(uid))
    elif d == "menu_engines":
        bot.edit_message_text("⚙️ **SELECT NEURAL ENGINE**", c.message.chat.id, c.message.message_id, reply_markup=get_engine_keyboard(uid))
    elif d.startswith("set_eng_"):
        eng = d.split("_")[2]
        db.update_config(uid, "engine", eng)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=get_engine_keyboard(uid))
    elif d == "toggle_deep":
        u = db.get_user_config(uid)
        db.update_config(uid, "deep_think", 0 if u['deep_think'] else 1)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=get_main_keyboard(uid))
    elif d.startswith("set_mode_"):
        mode = d.split("_")[2]
        db.update_config(uid, "mode", mode)
        bot.answer_callback_query(c.id, f"✅ Mode: {mode.upper()}")
    elif d == "trigger_swarm":
        msg = bot.send_message(c.message.chat.id, "👥 Topic for Swarm Intelligence:")
        bot.register_next_step_handler(msg, lambda m: run_swarm_protocol(uid, m.text, m.chat.id))
    elif d == "tool_pdf":
        msg = bot.send_message(c.message.chat.id, "📕 Topic for PDF Generation:")
        bot.register_next_step_handler(msg, handle_pdf_req)
    elif d == "tool_zip":
        msg = bot.send_message(c.message.chat.id, "📦 Requirement for ZIP Project:")
        bot.register_next_step_handler(msg, handle_zip_req)

def handle_pdf_req(m):
    mid = bot.send_message(m.chat.id, "⚙️ Generating PDF...").message_id
    buf = generate_pdf_document(m.from_user.id, m.text)
    buf.name = "MI_TITAN_REPORT.pdf"
    bot.send_document(m.chat.id, buf)
    bot.delete_message(m.chat.id, mid)

def handle_zip_req(m):
    mid = bot.send_message(m.chat.id, "⚙️ Building ZIP...").message_id
    buf = generate_zip_project(m.from_user.id, m.text)
    buf.name = "MI_TITAN_PROJECT.zip"
    bot.send_document(m.chat.id, buf)
    bot.delete_message(m.chat.id, mid)

# --- 👁️ TITAN VISION HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    uid = m.from_user.id
    mid = bot.reply_to(m, f"{ICONS['loading']} Analyzing visual nodes...").message_id
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        downloaded = bot.download_file(f_info.file_path)
        b64 = base64.b64encode(downloaded).decode()
        caption = m.caption or "Explain this image."
        ans, node = call_ai_titan(uid, caption, image_b64=b64)
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"👁️ **TITAN VISION**\n━━━━━━━━━━\n{ans}\n\n`Node: {node}`")
    except Exception as e:
        bot.edit_message_text(f"⚠️ Error: {e}", m.chat.id, mid)

# --- 🌍 UNIVERSAL MESSAGE ROUTER (FOR GROUPS & PRIVATES) ---
@bot.message_handler(func=lambda m: True)
def universal_handler(m):
    uid = m.from_user.id
    text = m.text
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    u = db.get_user_config(uid)

    # 1. ADMIN BROADCAST
    if text.startswith("/broadcast") and u['is_admin']:
        msg_to_send = text.replace("/broadcast", "").strip()
        db.c.execute("SELECT uid FROM users")
        all_users = db.c.fetchall()
        for user in all_users:
            try: bot.send_message(user[0], f"📢 **ADMIN ANNOUNCEMENT**\n\n{msg_to_send}")
            except: pass
        return bot.reply_to(m, "✅ Broadcast Sent Successfully.")

    # 2. GROUP/CHANNEL LOGIC
    # Reacts to EVERY message if in a group
    if m.chat.type != 'private':
        # Add a 20% randomness or check if it's a direct question to save tokens
        # Or respond to EVERYTHING as requested.
        ans, node = call_ai_titan(uid, text)
        bot.reply_to(m, f"🤖 {ans}")
        return

    # 3. PRIVATE CHAT LOGIC
    mid = bot.reply_to(m, f"{ICONS['loading']} Neural processing...").message_id
    
    if u['mode'] == 'search':
        final_ans = live_web_search(uid, text)
    else:
        ans, node = call_ai_titan(uid, text)
        final_ans = (
            f"**MI AI TITAN** | `{node}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{ans}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 _Powered by Muslim Islam_"
        )

    bot.delete_message(m.chat.id, mid)
    if len(final_ans) > 4000:
        for i in range(0, len(final_ans), 4000): bot.send_message(m.chat.id, final_ans[i:i+4000])
    else: bot.send_message(m.chat.id, final_ans, parse_mode="Markdown")

# ================= 🚀 SERVER INFINITY POLLING =================
if __name__ == "__main__":
    print("\n" + "═"*50)
    print("🔥 MI AI TITAN V15.0 ENTERPRISE SERVER STARTED 🔥")
    print("👨‍💻 Developed by: Muaaz Iqbal | MiTV Network")
    print("═"*50 + "\n")
    setup_digital_side_menu()
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Titan Crashed: {e}. Rebooting in 5s...")
            time.sleep(5)
