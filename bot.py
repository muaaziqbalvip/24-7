# ==============================================================================
# 👑 MI AI - PUBLIC ENTERPRISE EDITION (THE TITAN V13.0)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 🚀 STATUS: HIGHLY CLASSIFIED, AUTO-PILOT & PRODUCTION READY
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
import io
import zipfile
import sqlite3
import logging
import re
import random
from datetime import datetime
from fpdf import FPDF
from duckduckgo_search import DDGS
from functools import wraps

# ================= ⚙️ SYSTEM CONFIGURATION & ADVANCED LOGGING =================
# Logging is essential for enterprise backends so it doesn't "jam" silently.
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - MI AI CORE [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("mi_ai_system_v13.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 🔐 API KEYS (ENVIRONMENT VARIABLES ARE SECURE) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR_HF_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MuaazIqbal/MI-AI-Knowledge")

# --- 👑 ADMIN CONFIG ---
ADMIN_PASSCODE = "123456"
MASTER_ADMIN_ID = None  # Sets when passcode is used

# Threading active to handle hundreds of users without jamming
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=50)

# ================= CUSTOM EMOJIS & CONSTANTS =================
ICONS = {
    "bot": "🤖", "user": "👤", "gemini": "💎", "groq": "⚡", 
    "openrouter": "🌌", "hf": "🤗", "think": "🧠", "vision": "👁️", 
    "search": "🌐", "success": "✅", "loading": "⏳", "error": "⚠️", 
    "creator": "👨‍💻", "star": "🌟", "fire": "🔥", "code": "💻", 
    "story": "📖", "settings": "⚙️", "pdf": "📕", "zip": "📦", "github": "🐙"
}

# Session memory for states, temp files, and multi-step inputs
user_sessions = {} 

# ================= 🗄️ MASSIVE SQLITE DATABASE MANAGER =================
class MIDatabaseManager:
    """Handles all offline storage, user profiles, and chat logs."""
    def __init__(self, db_name='mi_ai_enterprise_v13.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.c = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # Users Table
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, name TEXT, username TEXT,
            education TEXT, city TEXT, purpose TEXT, phone TEXT,
            engine TEXT, mode TEXT, deep_think INTEGER DEFAULT 0,
            total_queries INTEGER, joined_date TEXT, last_active TEXT, 
            is_registered INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0
        )''')
        # Community Logs Table
        self.c.execute('''CREATE TABLE IF NOT EXISTS community_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, chat_type TEXT,
            user_id INTEGER, username TEXT, message TEXT, ai_reply TEXT, timestamp TEXT
        )''')
        # Agent Knowledge Base
        self.c.execute('''CREATE TABLE IF NOT EXISTS agent_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, content TEXT, timestamp TEXT
        )''')
        self.conn.commit()
        logger.info("Database Tables Initialized Successfully.")

    # --- User Management ---
    def is_registered(self, uid):
        self.c.execute("SELECT is_registered FROM users WHERE uid=?", (uid,))
        res = self.c.fetchone()
        return res[0] == 1 if res else False

    def init_user(self, uid, name, username):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute('''INSERT OR IGNORE INTO users 
            (uid, name, username, engine, mode, total_queries, joined_date, last_active, is_registered) 
            VALUES (?, ?, ?, 'gemini', 'chat', 0, ?, ?, 0)''', 
            (uid, name, username, date_now, date_now))
        self.conn.commit()

    def update_step(self, uid, column, value):
        self.c.execute(f"UPDATE users SET {column}=? WHERE uid=?", (value, uid))
        self.conn.commit()
    
    def get_user(self, uid):
        self.c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        row = self.c.fetchone()
        if row:
            return {
                "uid": row[0], "name": row[1], "username": row[2], "engine": row[7],
                "mode": row[8], "deep_think": row[9], "queries": row[10]
            }
        return None

    def update_activity(self, uid):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("UPDATE users SET total_queries = total_queries + 1, last_active = ? WHERE uid=?", (date_now, uid))
        self.conn.commit()

    def log_community(self, chat_id, chat_type, user_id, username, text, ai_reply="None"):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute('''INSERT INTO community_logs 
            (chat_id, chat_type, user_id, username, message, ai_reply, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (chat_id, chat_type, user_id, username, text, ai_reply, date_now))
        self.conn.commit()

db = MIDatabaseManager()

# ================= 🐙 GITHUB KNOWLEDGE SYNC ENGINE =================
def sync_knowledge_to_github(topic, content):
    """Saves AI Agent discussions directly to GitHub repo as Markdown."""
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        logger.warning("GitHub Token missing. Saving locally only.")
        return False
        
    safe_topic = re.sub(r'\W+', '_', topic.lower()[:20])
    file_path = f"knowledge_base/MI_Brain_{safe_topic}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        # Check if file exists to get SHA for updating
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        
        md_content = f"# MI AI Knowledge: {topic}\n\n**Generated by:** Muaaz Iqbal's Swarm Intelligence\n**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n{content}"
        content_b64 = base64.b64encode(md_content.encode('utf-8')).decode('utf-8')
        
        payload = {"message": f"🤖 Auto-Sync Knowledge: {topic}", "content": content_b64}
        if sha: payload["sha"] = sha
        
        r = requests.put(url, headers=headers, json=payload)
        if r.status_code in [200, 201]:
            logger.info(f"✅ GitHub Sync Success: {file_path}")
            return True
        else:
            logger.error(f"GitHub Sync Failed: {r.text}")
            return False
    except Exception as e:
        logger.error(f"GitHub API Exception: {e}")
        return False

# ================= PROMPT ENGINEERING SYSTEM =================
def build_system_prompt(uid, custom_role=None):
    user = db.get_user(uid)
    mode = user['mode'] if user else 'chat'
    deep = user['deep_think'] if user else 0
    
    base = (
        "Tumhara naam 'MI AI Enterprise' hai. Tumhe MUAAZ IQBAL ne banaya hai.\n"
        "Muaaz Iqbal MUSLIM ISLAM organization chalata hai. Tum ek highly advanced AI ho.\n"
        "Language: Roman Urdu and English. Use formatting and emojis heavily.\n"
    )
    
    if custom_role:
        base += f"CURRENT DIRECTIVE/ROLE: {custom_role}\n"
        
    if deep == 1:
        base += "[DEEP THINK MODE]: Analyze everything step-by-step. Provide massive detail, logic, and expert reasoning.\n"
        
    if mode == "code":
        base += "[CODE LAB MODE]: Only provide working, optimized, and heavily commented code blocks.\n"
    elif mode == "story":
        base += "[STORY MODE]: Write cinematic, highly detailed and engaging stories with chapters.\n"
        
    return base

def extract_api_text(res_dict, provider):
    """Safely parses JSON responses from different APIs to prevent crashes."""
    try:
        if provider == "gemini":
            return res_dict['candidates'][0]['content']['parts'][0]['text']
        elif provider in ["groq", "openrouter"]:
            return res_dict['choices'][0]['message']['content']
        elif provider == "hf":
            return res_dict[0]['generated_text'].split("[/INST]")[-1].strip()
    except Exception as e:
        logger.error(f"Text Extraction Failed for {provider}: {e}")
        return None

# ================= 🚀 THE MULTI-NODE AI CORE =================
def quantum_ai_brain(uid, prompt, custom_role=None, img_data_b64=None, force_engine=None):
    """
    The Ultimate Router. 
    It checks user preferences, applies fallbacks, and processes data.
    """
    db.update_activity(uid)
    user = db.get_user(uid)
    
    # Engine Selection Logic
    engine = force_engine if force_engine else (user['engine'] if user else "gemini")
    deep_think = user['deep_think'] if user else 0
    sys_prompt = build_system_prompt(uid, custom_role)
    
    # 1. 👁️ VISION OVERRIDE (Forces Gemini)
    if img_data_b64:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": f"System: {sys_prompt}\nUser: {prompt}"}, {"inline_data": {"mime_type": "image/jpeg", "data": img_data_b64}}]}]}
            r = requests.post(url, json=payload, timeout=40).json()
            return extract_api_text(r, "gemini"), "Gemini Vision 👁️"
        except Exception as e:
            return f"⚠️ Vision Protocol Failed: {e}", "Error"

    # --- MAIN TEXT ROUTING WITH FALLBACKS ---
    response = None
    used_node = None

    try:
        # Node A: GROQ (Speed King)
        if engine == "groq" and not response:
            model = "llama-3.3-70b-versatile" if deep_think else "llama3-8b-8192"
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, 
                json={"model": model, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]},
                timeout=20).json()
            response = extract_api_text(r, "groq")
            used_node = f"Groq ({model}) ⚡"

        # Node B: HUGGING FACE (Mistral)
        if engine == "hf" and not response:
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            r = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, 
                json={"inputs": f"<s>[INST] {sys_prompt}\n{prompt} [/INST]", "parameters": {"max_new_tokens": 1500}},
                timeout=30).json()
            response = extract_api_text(r, "hf")
            used_node = "HF Mistral 🤗"

        # Node C: OPENROUTER (GPT Backup)
        if engine == "openrouter" and not response:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}, 
                json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]},
                timeout=30).json()
            response = extract_api_text(r, "openrouter")
            used_node = "OpenRouter 🌌"

        # Node D: GEMINI (Default & Ultimate Fallback)
        if (engine == "gemini" or not response):
            model = "gemini-1.5-pro" if deep_think else "gemini-1.5-flash"
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}", 
                json={"contents": [{"parts": [{"text": f"System: {sys_prompt}\nUser: {prompt}"}]}]},
                timeout=30).json()
            response = extract_api_text(r, "gemini")
            used_node = f"Gemini ({model}) 💎"

    except Exception as e:
        logger.error(f"Core Engine Error: {e}")
        return "⚠️ All AI nodes are currently jammed or overloaded. Apologies.", "System Failure"

    return response, used_node

# ================= 🤖 AGENT SWARM (COMMUNITY BOT SYSTEM) =================
def agent_meeting_protocol(uid, topic):
    """AI models talking to each other to generate a master document."""
    # Step 1: Gemini researches
    t1 = time.time()
    res1, n1 = quantum_ai_brain(uid, f"Research and provide core unformatted facts about: {topic}", force_engine="gemini")
    
    # Step 2: Groq expands
    res2, n2 = quantum_ai_brain(uid, f"Critique and deeply expand on these facts technically:\n{res1}", force_engine="groq")
    
    # Step 3: HF formats for humans
    final_res, n3 = quantum_ai_brain(uid, f"Take this data and format it into a beautiful, engaging Roman Urdu/English master guide:\n{res2}", force_engine="openrouter")
    
    # Save to GitHub
    synced = sync_knowledge_to_github(topic, final_res)
    sync_status = "✅ Synced to GitHub" if synced else "⚠️ Local Storage Only"
    
    report = (
        f"👥 **AI SWARM MEETING COMPLETE** 👥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**Topic:** {topic}\n"
        f"**Node 1 (Researcher):** {n1}\n"
        f"**Node 2 (Expander):** {n2}\n"
        f"**Node 3 (Formatter):** {n3}\n"
        f"**Status:** {sync_status}\n"
        f"**Time Taken:** {round(time.time()-t1, 2)}s\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{final_res}"
    )
    return report

# ================= 🌐 LIVE WEB SEARCH (DUCKDUCKGO) =================
def live_web_search(uid, query):
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=5)
        raw_data = ""
        for r in results: 
            raw_data += f"Title: {r.get('title')}\nLink: {r.get('href')}\nDetail: {r.get('body')}\n\n"
        
        ai_prompt = f"User searched: {query}. Live Internet Data:\n{raw_data}\nSummarize this data into an accurate, highly readable report."
        ans, node = quantum_ai_brain(uid, ai_prompt, custom_role="Live Internet Researcher")
        return f"🌐 **LIVE SEARCH RESULTS**\n━━━━━━━━━━━━━━━━━━━━━━\n{ans}\n\n`Source: DuckDuckGo | Node: {node}`"
    except Exception as e:
        return f"⚠️ Search Engine Jammed: {e}"

# ================= 🎨 PDF & ZIP ARCHITECT =================
class MIPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'MI AI ENTERPRISE - MUAAZ IQBAL - MUSLIM ISLAM', 0, 1, 'C')
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_color_pdf(uid, topic):
    content, _ = quantum_ai_brain(uid, f"Write a comprehensive multi-page book chapter on '{topic}'. Clean text only, no complex markdown.", custom_role="Author")
    
    pdf = MIPDF()
    pdf.add_page()
    pdf.set_fill_color(20, 20, 30) 
    pdf.rect(0, 0, 210, 297, 'F')
    
    pdf.set_text_color(0, 255, 150)
    pdf.set_font("Arial", 'B', 30)
    pdf.text(20, 120, "MI AI ENTERPRISE")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_xy(20, 150)
    pdf.multi_cell(170, 10, topic.upper(), align='C')
    
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Arial", size=12)
    clean_text = content.replace('”', '"').replace('“', '"').replace('*', '').encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_text)
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def build_zip_project(uid, prompt):
    sys_req = "Generate a full coding project. Format strictly: <<<FILE: filename.ext>>>\ncode here\n<<<ENDFILE>>>"
    raw_code, _ = quantum_ai_brain(uid, prompt, custom_role=sys_req)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        matches = re.findall(r'<<<FILE:\s*(.+?)>>>(.*?)(?:<<<ENDFILE>>>|\Z)', raw_code, re.DOTALL)
        if matches:
            for fname, code in matches: z.writestr(fname.strip(), code.strip())
        else:
            z.writestr("MI_Logic.txt", raw_code)
        z.writestr("README.md", f"# MI AI Generated Project\n**Author:** Muaaz Iqbal\n**Prompt:** {prompt}")
    buf.seek(0)
    return buf

# ================= 🎨 UI: MENUS & KEYBOARDS =================
def setup_telegram_menu():
    """Sets the native Telegram side menu button."""
    try:
        commands = [
            types.BotCommand("start", "Boot MI AI Enterprise"),
            types.BotCommand("menu", "Open Main Control Panel"),
            types.BotCommand("swarm", "Start AI Meeting (Community Mode)"),
            types.BotCommand("profile", "View your Database Profile"),
            types.BotCommand("help", "Get System Assistance")
        ]
        bot.set_my_commands(commands)
        logger.info("Telegram Native Menu Installed.")
    except Exception as e:
        logger.error(f"Menu Setup Error: {e}")

def main_dashboard(uid):
    user = db.get_user(uid)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    deep_btn = "🧠 Deep Think: ON" if user and user['deep_think'] else "⚡ Fast Mode"
    
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['bot']} AI Chat", callback_data="mode_chat"),
        types.InlineKeyboardButton(f"{ICONS['settings']} Set AI Core", callback_data="menu_engines")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['search']} Live Web", callback_data="mode_search"),
        types.InlineKeyboardButton(deep_btn, callback_data="toggle_deep")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['story']} Story", callback_data="mode_story"),
        types.InlineKeyboardButton(f"{ICONS['code']} Code Lab", callback_data="mode_code")
    )
    markup.add(
        types.InlineKeyboardButton(f"{ICONS['pdf']} PDF Maker", callback_data="tool_pdf"),
        types.InlineKeyboardButton(f"{ICONS['zip']} ZIP Gen", callback_data="tool_zip")
    )
    markup.add(types.InlineKeyboardButton(f"{ICONS['github']} Start Swarm Meeting", callback_data="tool_swarm"))
    return markup

def engine_menu(uid):
    u = db.get_user(uid)
    curr = u['engine'] if u else 'gemini'
    m = types.InlineKeyboardMarkup(row_width=1)
    
    m.add(types.InlineKeyboardButton(f"{ICONS['gemini']} Gemini Core" + (" ✅" if curr=='gemini' else ""), callback_data="eng_gemini"))
    m.add(types.InlineKeyboardButton(f"{ICONS['groq']} Groq Llama" + (" ✅" if curr=='groq' else ""), callback_data="eng_groq"))
    m.add(types.InlineKeyboardButton(f"{ICONS['hf']} HF Mistral" + (" ✅" if curr=='hf' else ""), callback_data="eng_hf"))
    m.add(types.InlineKeyboardButton(f"{ICONS['openrouter']} OpenRouter" + (" ✅" if curr=='openrouter' else ""), callback_data="eng_openrouter"))
    m.add(types.InlineKeyboardButton("🔙 Back to Dashboard", callback_data="go_dash"))
    return m

# ================= 🤖 BOT HANDLERS & ROUTERS =================

def animated_loading(chat_id, msg_id, task="Processing"):
    frames = [f"⏳ {task}.", f"🧠 {task}..", f"⚙️ {task}...", f"⚡ {task}...."]
    for _ in range(2):
        for f in frames:
            try:
                bot.edit_message_text(f, chat_id, msg_id)
                time.sleep(0.4)
            except: pass

def send_long(chat_id, text):
    """Prevents crashing on large messages."""
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            bot.send_message(chat_id, text[x:x+4000], parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.message_handler(commands=['start', 'menu', 'profile', 'swarm'])
def handle_commands(m):
    uid = m.from_user.id
    cmd = m.text.replace('/', '').split()[0]
    
    db.init_user(uid, m.from_user.first_name, m.from_user.username)
    
    if not db.is_registered(uid) and cmd == 'start':
        user_sessions[uid] = {'state': 'reg_edu'}
        bot.send_message(m.chat.id, "🌟 **MI AI REGISTRATION** 🌟\nWhat is your education level?")
        return

    if cmd in ['start', 'menu']:
        bot.send_message(m.chat.id, f"🌟 **MI AI ENTERPRISE V13.0**\nWelcome back, {m.from_user.first_name}!", reply_markup=main_dashboard(uid))
    
    elif cmd == 'profile':
        u = db.get_user(uid)
        bot.send_message(m.chat.id, f"📊 **PROFILE**\nEngine: {u['engine'].upper()}\nMode: {u['mode'].upper()}\nQueries: {u['queries']}")
        
    elif cmd == 'swarm':
        msg = bot.send_message(m.chat.id, "👥 **SWARM MODE**\nEnter a topic for the AIs to discuss and save to GitHub:")
        bot.register_next_step_handler(msg, execute_swarm)

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    uid = c.from_user.id
    d = c.data
    
    if d == "go_dash":
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=main_dashboard(uid))
    elif d == "menu_engines":
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=engine_menu(uid))
    
    elif d.startswith("eng_"):
        db.update_step(uid, 'engine', d.split('_')[1])
        bot.answer_callback_query(c.id, "✅ Engine Updated")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=engine_menu(uid))
        
    elif d == "toggle_deep":
        u = db.get_user(uid)
        new_val = 0 if u['deep_think'] == 1 else 1
        db.update_step(uid, 'deep_think', new_val)
        bot.answer_callback_query(c.id, "🧠 Deep Think Toggled")
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=main_dashboard(uid))
        
    elif d.startswith("mode_"):
        mode = d.split('_')[1]
        db.update_step(uid, 'mode', mode)
        bot.answer_callback_query(c.id, f"{mode.upper()} Mode Activated")
        bot.send_message(c.message.chat.id, f"✅ **{mode.upper()} Mode is now active.** Send your prompt.")
        
    elif d == "tool_pdf":
        msg = bot.send_message(c.message.chat.id, "📕 Enter topic for PDF Book:")
        bot.register_next_step_handler(msg, lambda m: execute_complex(m, "pdf"))
    elif d == "tool_zip":
        msg = bot.send_message(c.message.chat.id, "📦 Enter details for ZIP Code Generation:")
        bot.register_next_step_handler(msg, lambda m: execute_complex(m, "zip"))
    elif d == "tool_swarm":
        msg = bot.send_message(c.message.chat.id, "👥 Enter topic for Swarm Meeting:")
        bot.register_next_step_handler(msg, execute_swarm)

# --- COMPLEX EXECUTORS ---
def execute_swarm(m):
    mid = bot.send_message(m.chat.id, "🔄 Connecting Neural Nodes...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid, "Agents Discussing")).start()
    report = agent_meeting_protocol(m.from_user.id, m.text)
    bot.delete_message(m.chat.id, mid)
    send_long(m.chat.id, report)

def execute_complex(m, task):
    mid = bot.send_message(m.chat.id, f"⚙️ Generating {task.upper()}...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid, f"Building {task}")).start()
    try:
        if task == "pdf":
            buf = generate_color_pdf(m.from_user.id, m.text)
            buf.name = "MI_AI_Book.pdf"
            bot.send_document(m.chat.id, buf)
        elif task == "zip":
            buf = build_zip_project(m.from_user.id, m.text)
            buf.name = "MI_Project.zip"
            bot.send_document(m.chat.id, buf)
    except Exception as e:
        bot.send_message(m.chat.id, f"⚠️ Error: {e}")
    finally:
        bot.delete_message(m.chat.id, mid)

# --- IMAGE HANDLER ---
@bot.message_handler(content_types=['photo'])
def handle_image(m):
    mid = bot.reply_to(m, "👁️ Extracting visual data...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid, "Vision Scan")).start()
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        b64 = base64.b64encode(img_data).decode('utf-8')
        
        prompt = m.caption if m.caption else "Describe this image technically."
        ans, node = quantum_ai_brain(m.from_user.id, prompt, img_data_b64=b64)
        
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"👁️ **VISION REPORT**\n━━━━━━━━━━\n{ans}\n\n`Node: {node}`", parse_mode="Markdown")
    except Exception as e:
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "⚠️ Vision failure. Gemini might be overloaded.")

# --- MASTER TEXT ROUTER (INCLUDING GROUPS/CHANNELS) ---
@bot.message_handler(func=lambda m: True)
def master_text_router(m):
    uid = m.from_user.id
    txt = m.text

    # 1. Registration Trap
    if uid in user_sessions and user_sessions[uid].get('state') == 'reg_edu':
        db.update_step(uid, 'education', txt)
        db.update_step(uid, 'is_registered', 1)
        del user_sessions[uid]
        bot.send_message(m.chat.id, "✅ Registration Complete! Type /menu")
        return

    # 2. Admin Broadcast Trap
    if txt == ADMIN_PASSCODE:
        global MASTER_ADMIN_ID
        MASTER_ADMIN_ID = uid
        return bot.reply_to(m, "👑 Master Admin Access Granted.\nSend `/broadcast [msg]` to message all.")
    
    if txt.startswith('/broadcast') and uid == MASTER_ADMIN_ID:
        msg = txt.replace('/broadcast ', '')
        db.c.execute("SELECT uid FROM users")
        for u in db.c.fetchall():
            try: bot.send_message(u[0], f"📢 **ADMIN ALERT:**\n{msg}")
            except: pass
        return bot.reply_to(m, "✅ Broadcast Sent.")

    # 3. 📢 AUTO-CHANNEL POSTING
    if m.chat.type == "channel":
        if "post" in txt.lower():
            ans, _ = quantum_ai_brain(uid, "Write a high-quality, viral tech/islamic educational post.", custom_role="Social Manager")
            bot.send_message(m.chat.id, f"🌟 **MI AI DAILY INSIGHT** 🌟\n\n{ans}")
        return

    # 4. 👥 AUTO-GROUP CHATTING
    if m.chat.type in ["group", "supergroup"]:
        # Log everything for AI memory
        db.log_community(m.chat.id, m.chat.type, uid, m.from_user.username, txt)
        
        # If directly tagged or 5% chance to interrupt naturally
        if "mi ai" in txt.lower() or "muaaz" in txt.lower():
            ans, node = quantum_ai_brain(uid, f"Group member asked: {txt}. Reply nicely.")
            db.log_community(m.chat.id, m.chat.type, uid, "MI_AI_REPLY", "REPLY", ans)
            bot.reply_to(m, f"🤖 {ans}\n`[{node}]`")
        elif random.random() < 0.05:
            ans, _ = quantum_ai_brain(uid, f"Context: {txt}. Say something very brief and witty.", custom_role="Group Friend")
            bot.send_message(m.chat.id, f"🧠 Just thinking: {ans}")
        return

    # 5. PRIVATE DIRECT MESSAGE PROCESSING
    u = db.get_user(uid)
    if not u: return bot.reply_to(m, "Type /start to register.")

    mid = bot.send_message(m.chat.id, "🔄 Processing via Quantum Core...").message_id
    threading.Thread(target=animated_loading, args=(m.chat.id, mid)).start()
    
    try:
        if u['mode'] == 'search':
            final_res = live_web_search(uid, txt)
        else:
            ans, node = quantum_ai_brain(uid, txt)
            final_res = f"🧠 **MI AI RESPONSE**\n━━━━━━━━━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Engine:* `{node}`"
        
        bot.delete_message(m.chat.id, mid)
        send_long(m.chat.id, final_res)
    except Exception as e:
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"⚠️ System Exception: {e}")

# ================= 🚀 SERVER INITIALIZATION =================
if __name__ == "__main__":
    print("\n" + "═"*70)
    print("🔥 MI AI MEGA ENTERPRISE EDITION V13.0 IS ONLINE 🔥")
    print("👨‍💻 Architect: Muaaz Iqbal | Organization: Muslim Islam")
    print("🌐 Modules Loaded:")
    print("   ✅ SQLite DB & Native Side Menus")
    print("   ✅ Agent Swarm & GitHub Auto-Sync")
    print("   ✅ Auto-Pilot Channel & Group Chatting")
    print("   ✅ Quad-Node AI System (Gemini, Groq, HF, OpenRouter)")
    print("═"*70 + "\n")
    
    setup_telegram_menu()
    
    # Robust Infinity Polling
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Polling Crashed: {e}. Rebooting in 5s...")
            time.sleep(5)
