# ==============================================================================
# 👑 MI AI - PUBLIC ENTERPRISE EDITION (THE MEGA BOMB V12.0)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 🚀 STATUS: HIGHLY CLASSIFIED & PRODUCTION READY
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
from PIL import Image

# ================= ⚙️ SYSTEM CONFIGURATION & ADVANCED LOGGING =================
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - MI AI CORE [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("mi_ai_system.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 🔐 API KEYS (ALL FROM ENVIRONMENT VARIABLES NOW) ---
# HF_TOKEN ab baqi keys ki tarah variable mein hai!
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR_HF_TOKEN_HERE") 

# --- 👑 ADMIN CONFIG ---
ADMIN_PASSCODE = "123456"
MASTER_ADMIN_ID = None  # Auto-sets when Muaaz enters passcode

# Multi-threading active for fast concurrent processing
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=30)

# ================= 🗄️ MASSIVE SQLITE DATABASE MANAGER =================
class MIDatabaseManager:
    def __init__(self, db_name='mi_ai_enterprise_v12.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.c = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # 1. Users Table (Detailed Registration)
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, name TEXT, username TEXT,
            education TEXT, city TEXT, purpose TEXT, phone TEXT,
            engine TEXT, mode TEXT, total_queries INTEGER,
            joined_date TEXT, last_active TEXT, is_registered INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0, vip_status INTEGER DEFAULT 0
        )''')
        # 2. Community Logs Table (Group Chats)
        self.c.execute('''CREATE TABLE IF NOT EXISTS community_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER, group_name TEXT,
            user_id INTEGER, username TEXT, message TEXT, ai_reply TEXT, timestamp TEXT
        )''')
        # 3. Media History (Images, PDFs, ZIPs)
        self.c.execute('''CREATE TABLE IF NOT EXISTS media_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
            media_type TEXT, prompt TEXT, timestamp TEXT
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
            VALUES (?, ?, ?, 'groq', 'chat', 0, ?, ?, 0)''', 
            (uid, name, username, date_now, date_now))
        self.conn.commit()

    def update_registration_step(self, uid, column, value):
        self.c.execute(f"UPDATE users SET {column}=? WHERE uid=?", (value, uid))
        self.conn.commit()

    def complete_registration(self, uid):
        self.c.execute("UPDATE users SET is_registered=1 WHERE uid=?", (uid,))
        self.conn.commit()
    
    def get_user(self, uid):
        self.c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        return self.c.fetchone()

    def update_activity(self, uid):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("UPDATE users SET total_queries = total_queries + 1, last_active = ? WHERE uid=?", (date_now, uid))
        self.conn.commit()
    
    def update_engine(self, uid, engine):
        self.c.execute("UPDATE users SET engine=? WHERE uid=?", (engine, uid))
        self.conn.commit()

    # --- Community Logs ---
    def log_group_activity(self, chat_id, chat_title, user_id, username, text, ai_reply="None"):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute('''INSERT INTO community_logs 
            (group_id, group_name, user_id, username, message, ai_reply, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (chat_id, chat_title, user_id, username, text, ai_reply, date_now))
        self.conn.commit()
        
    def log_media(self, user_id, media_type, prompt):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.c.execute("INSERT INTO media_history (user_id, media_type, prompt, timestamp) VALUES (?, ?, ?, ?)", (user_id, media_type, prompt, date_now))
        self.conn.commit()

db = MIDatabaseManager()

# Session memory to track states, temp files, and flows
user_sessions = {} 

# ================= 🎨 ADVANCED UI ANIMATION ENGINE =================
class AdvancedAnimator:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.animations = {
            "radar": ["📡 [ ◯ ◯ ◯ ]", "📡 [ ◉ ◯ ◯ ]", "📡 [ ◯ ◉ ◯ ]", "📡 [ ◯ ◯ ◉ ]", "📡 [ ◉ ◉ ◉ ]"],
            "blocks": ["⬛⬜⬜⬜⬜", "🟩⬛⬜⬜⬜", "🟩🟩⬛⬜⬜", "🟩🟩🟩⬛⬜", "🟩🟩🟩🟩⬛", "🟩🟩🟩🟩🟩"],
            "matrix": ["░░░░░ 0%", "▓░░░░ 20%", "▓▓░░░ 40%", "▓▓▓░░ 60%", "▓▓▓▓░ 80%", "▓▓▓▓▓ 100%"],
            "hack": ["⚙️ 0x0001", "⚙️ 0x00A4", "⚙️ 0x0B8F", "⚙️ 0x1C9A", "⚙️ ACCESS GRANTED"],
            "video": ["🎥 [>     ]", "🎥 [=>    ]", "🎥 [==>   ]", "🎥 [===>  ]", "🎥 [====> ]"]
        }

    def play(self, chat_id, text, anim_type="blocks", speed=0.4, loops=1):
        msg = self.bot.send_message(chat_id, f"⚡ **{text}**\n{self.animations[anim_type][0]}", parse_mode="Markdown")
        frames = self.animations.get(anim_type, self.animations["blocks"])
        
        for _ in range(loops):
            for frame in frames:
                try:
                    self.bot.edit_message_text(
                        f"🔮 **MI AI QUANTUM CORE**\n━━━━━━━━━━━━━━\n🌀 *Task:* `{text}`\n📊 *Status:* {frame}\n*Please wait...*",
                        chat_id, msg.message_id, parse_mode="Markdown"
                    )
                    time.sleep(speed)
                except: pass
        return msg.message_id

animator = AdvancedAnimator(bot)

# ================= 🎛️ DYNAMIC MENUS & KEYBOARDS =================
def public_dashboard():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(types.KeyboardButton("⚡ Fast AI Chat"), types.KeyboardButton("🌐 Live Web Search"))
    m.add(types.KeyboardButton("🎨 HF Art Studio"), types.KeyboardButton("💻 Mega Code Lab"))
    m.add(types.KeyboardButton("📕 Color PDF Book"), types.KeyboardButton("📦 ZIP Architect"))
    m.add(types.KeyboardButton("🎥 Video & Media"), types.KeyboardButton("👁️ Vision Analysis"))
    m.add(types.KeyboardButton("⚙️ Control Panel"), types.KeyboardButton("📊 My Profile"))
    return m

def control_panel_menu(uid):
    u_data = db.get_user(uid)
    engine = u_data[7].upper() if u_data else "UNKNOWN"
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton(f"🟢 Active Engine: {engine}", callback_data="none"))
    m.add(types.InlineKeyboardButton("⚡ Groq Llama-3 (Fastest)", callback_data="ai_groq"))
    m.add(types.InlineKeyboardButton("💎 Gemini 1.5 (Deep Vision)", callback_data="ai_gemini"))
    m.add(types.InlineKeyboardButton("🤗 HF Mistral (Creative)", callback_data="ai_hf"))
    m.add(types.InlineKeyboardButton("🌌 OpenRouter (GPT/Claude)", callback_data="ai_openrouter"))
    return m

# ================= 🚀 QUANTUM 4-AI ENGINE CORE =================
def extract_clean_text(response_dict, provider):
    """Utility to safely extract text from different API response structures."""
    try:
        if provider == "gemini":
            return response_dict['candidates'][0]['content']['parts'][0]['text']
        elif provider in ["groq", "openrouter"]:
            return response_dict['choices'][0]['message']['content']
        elif provider == "hf":
            return response_dict[0]['generated_text'].split("[/INST]")[-1].strip()
    except Exception as e:
        logger.error(f"Extraction Error for {provider}: {e}")
        return None

def mega_ai_brain(uid, prompt, sys_role="Super AI Assistant", img_path=None):
    db.update_activity(uid)
    user_data = db.get_user(uid)
    engine = user_data[7] if user_data else "groq"
    sys_prompt = f"Your name is MI AI. Creator: Muaaz Iqbal. Role: {sys_role}. Organization: MUSLIM ISLAM. Be highly professional, use markdown formatting, use emojis, and be highly accurate."

    try:
        # 1. 👁️ VISION OVERRIDE: Image always forces Gemini API
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            payload = {"contents": [{"parts": [{"text": f"{sys_prompt}\nUser: {prompt}"}, {"inline_data": {"mime_type": "image/jpeg", "data": encoded_string}}]}]}
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}", json=payload).json()
            return extract_clean_text(res, "gemini"), "Gemini Vision 👁️"

        # 2. ⚡ GROQ (SPEED KING)
        if engine == "groq":
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {GROQ_KEY}"}, 
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}
            ).json()
            return extract_clean_text(res, "groq"), "Groq 70B ⚡"
            
        # 3. 🤗 HUGGING FACE (MISTRAL TEXT)
        elif engine == "hf":
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": f"<s>[INST] {sys_prompt}\n{prompt} [/INST]", "parameters": {"max_new_tokens": 1500, "temperature": 0.7}}
            res = requests.post(url, headers=headers, json=payload).json()
            return extract_clean_text(res, "hf"), "HF Mistral 🤗"
            
        # 4. 🌌 OPENROUTER (GPT/CLAUDE BACKUP)
        elif engine == "openrouter":
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"}, 
                json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}
            ).json()
            return extract_clean_text(res, "openrouter"), "OpenRouter 🌌"
            
        # 5. 💎 GEMINI DEFAULT (FLASH FOR SPEED)
        else: 
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}", 
                json={"contents": [{"parts": [{"text": f"{sys_prompt}\nUser: {prompt}"}]}]}
            ).json()
            return extract_clean_text(res, "gemini"), "Gemini Flash 💎"

    except Exception as e:
        logger.error(f"AI Engine Error in node {engine}: {e}")
        return f"⚠️ Engine `{engine}` overloaded. Switch engine from Control Panel.\nError Log: {str(e)[:100]}", "Error Node"

# ================= 🎨 HUGGING FACE IMAGE ENGINE (FLUX 2026) =================
def generate_hf_image(uid, prompt):
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        if response.status_code == 200:
            db.log_media(uid, "image", prompt)
            path = f"cache_art_{uid}_{random.randint(1000,9999)}.jpg"
            with open(path, "wb") as f: 
                f.write(response.content)
            return path
        else:
            logger.error(f"HF Image API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e: 
        logger.error(f"HF Image Exception: {e}")
        return None

# ================= 🌐 REAL DUCKDUCKGO WEB SEARCH & VIDEO SEARCH =================
def real_web_search(uid, query, mode="text"):
    try:
        ddgs = DDGS()
        raw_data = ""
        
        if mode == "video":
            # DuckDuckGo Video Search implementation
            results = ddgs.videos(query, max_results=5)
            for r in results: 
                raw_data += f"Video Title: {r.get('title')}\nURL: {r.get('content')}\nDuration: {r.get('duration')}\n\n"
            sys_role = "Video Search Analyst"
            ai_prompt = f"User searched for video: {query}. Extracted DDG data: {raw_data}. Give a structured list of these videos with titles, links, and a brief guess of what the video is about."
        else:
            # DuckDuckGo Text/News Search implementation
            results = ddgs.text(query, max_results=7)
            for r in results: 
                raw_data += f"Headline: {r.get('title')}\nLink: {r.get('href')}\nDetail: {r.get('body')}\n\n"
            sys_role = "Live Global Researcher"
            ai_prompt = f"User searched for: {query}. Live Internet Data: {raw_data}. Summarize this perfectly into a highly accurate, structured report. Add bullet points."

        # Pass live data to AI for formatting and summarization
        ai_report, node = mega_ai_brain(uid, ai_prompt, sys_role)
        return ai_report, node
    except Exception as e:
        logger.error(f"DDGS Search Error: {e}")
        return f"⚠️ Live Search Failed. The internet node might be blocked right now.\nError: {e}", "Search Node"

# ================= 📕 ADVANCED COLOR PDF PUBLISHER =================
class MIPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'MI AI ENTERPRISE - MUAAZ IQBAL - MUSLIM ISLAM', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def build_color_pdf(uid, topic, cover_img_path=None):
    # Ask AI to generate a full structured book chapter
    content, _ = mega_ai_brain(uid, f"Write a comprehensive, professional, multi-page book chapter on '{topic}'. Include Introduction, Core Concepts, Examples, and Conclusion. Format cleanly without heavy markdown symbols.", "Master Author")
    
    pdf = MIPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PAGE 1: LUXURY COVER PAGE ---
    pdf.add_page()
    pdf.set_fill_color(15, 20, 25) # Dark aesthetic bg
    pdf.rect(0, 0, 210, 297, 'F')
    
    if cover_img_path and os.path.exists(cover_img_path): 
        pdf.image(cover_img_path, x=20, y=40, w=170)
    else:
        pdf.set_text_color(0, 200, 255) # Cyan 
        pdf.set_font("Arial", 'B', 40)
        pdf.text(25, 120, "MI AI ENTERPRISE")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_xy(20, 170)
    pdf.multi_cell(170, 12, topic.upper(), align='C')
    
    pdf.set_font("Arial", size=14)
    pdf.set_xy(20, 220)
    pdf.multi_cell(170, 10, "Architect: Muaaz Iqbal\nPowered by MI AI V12.0", align='C')

    # --- PAGE 2+: CONTENT PAGES ---
    pdf.add_page()
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Arial", size=12)
    
    # Handle FPDF encoding issues safely
    clean_text = content.replace('”', '"').replace('“', '"').replace('’', "'").replace('*', '')
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 8, clean_text)
    
    db.log_media(uid, "pdf", topic)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# ================= 📦 MEGA ZIP ARCHITECT (CODE GEN) =================
def zip_project_builder(uid, req):
    sys_req = """You are a Senior Systems Architect. Generate a full modular codebase.
    CRITICAL INSTRUCTION: You MUST format your response EXACTLY like this for EVERY file:
    <<<FILE: filename.ext>>>
    code logic here
    <<<ENDFILE>>>
    Generate a main file, a utility file, and a README.md."""
    
    raw_code, _ = mega_ai_brain(uid, req, sys_req)
    db.log_media(uid, "zip_project", req)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Regex to extract files based on the strict delimiter
        matches = re.findall(r'<<<FILE:\s*(.+?)>>>(.*?)(?:<<<ENDFILE>>>|\Z)', raw_code, re.DOTALL)
        if matches:
            for fname, code in matches: 
                z.writestr(fname.strip(), code.strip())
        else: 
            z.writestr("MI_SourceCode.txt", raw_code) # Fallback if AI messes up format
            
        # Always inject a master README
        readme_content = f"# MI AI Generated Project\n\n**Architect:** Muaaz Iqbal\n**Project Prompt:** {req}\n**Organization:** MUSLIM ISLAM\n\n*Code automatically generated and packaged by MI AI V12.0*"
        z.writestr("README.md", readme_content)
        
    buf.seek(0)
    return buf

# ================= 📝 MULTI-STEP REGISTRATION FSM =================
def process_registration(m):
    uid = m.from_user.id
    state = user_sessions[uid].get('reg_state')
    
    if state == 'edu':
        db.update_registration_step(uid, 'education', m.text)
        user_sessions[uid]['reg_state'] = 'city'
        bot.send_message(m.chat.id, "🏙️ **Great! Which city are you located in?**")
    
    elif state == 'city':
        db.update_registration_step(uid, 'city', m.text)
        user_sessions[uid]['reg_state'] = 'purpose'
        bot.send_message(m.chat.id, "🎯 **Awesome! What is your main purpose for using MI AI? (e.g., Coding, Business, Studies)**")
        
    elif state == 'purpose':
        db.update_registration_step(uid, 'purpose', m.text)
        db.complete_registration(uid)
        user_sessions[uid]['reg_state'] = 'complete'
        
        bot.send_message(
            m.chat.id, 
            f"🎉 **REGISTRATION COMPLETE!**\n\nWelcome to the MI AI Enterprise Ecosystem, **{m.from_user.first_name}**.\nAll Neural Networks are now at your command.", 
            reply_markup=public_dashboard()
        )

# ================= 🤖 MAIN BOT ROUTERS & HANDLERS =================

@bot.message_handler(commands=['start', 'help'])
def start_public(m):
    uid = m.from_user.id
    db.init_user(uid, m.from_user.first_name, m.from_user.username)
    
    if uid not in user_sessions: 
        user_sessions[uid] = {"cover_img": None}

    if not db.is_registered(uid):
        user_sessions[uid]['reg_state'] = 'edu'
        welcome_text = (
            "🌟 **WELCOME TO MI AI REGISTRATION** 🌟\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "This is a Highly Advanced Private AI System created by **Muaaz Iqbal**.\n\n"
            "📚 **Step 1:** What is your highest education or current degree? (e.g., ICS, BSCS, Matric)"
        )
        bot.send_message(m.chat.id, welcome_text)
    else:
        bot.send_message(m.chat.id, f"🚀 **MI AI MAX PRO V12.0 ONLINE**\nWelcome back, Master {m.from_user.first_name}!\nAll systems nominal.", reply_markup=public_dashboard())

# --- 👑 MUAAZ IQBAL ADMIN CONTROL ---
@bot.message_handler(func=lambda m: m.text == ADMIN_PASSCODE)
def admin_login(m):
    global MASTER_ADMIN_ID
    MASTER_ADMIN_ID = m.from_user.id
    bot.reply_to(m, "👑 **MUAAZ IQBAL IDENTIFIED.**\nMaster Admin Mode Activated.\n\nCommands:\n`/db` - Download SQLite Database\n`/logs` - Download System Logs\n`/broadcast [msg]` - Send message to all users")

@bot.message_handler(commands=['db', 'logs', 'broadcast'])
def admin_commands(m):
    if m.from_user.id != MASTER_ADMIN_ID: 
        return bot.reply_to(m, "⚠️ Access Denied. Admin privilege required.")
        
    if m.text == '/db':
        if os.path.exists('mi_ai_enterprise_v12.db'):
            bot.send_document(m.chat.id, open('mi_ai_enterprise_v12.db', 'rb'), caption="📦 Core Database Backup")
    
    elif m.text == '/logs':
        if os.path.exists('mi_ai_system.log'):
            bot.send_document(m.chat.id, open('mi_ai_system.log', 'rb'), caption="⚙️ System Logs")
            
    elif m.text.startswith('/broadcast '):
        msg_to_send = m.text.replace('/broadcast ', '')
        bot.reply_to(m, f"📡 Broadcasting to all users... this may take time.")
        db.c.execute("SELECT uid FROM users")
        all_users = db.c.fetchall()
        success = 0
        for user in all_users:
            try:
                bot.send_message(user[0], f"📢 **ADMIN BROADCAST from Muaaz Iqbal:**\n\n{msg_to_send}")
                success += 1
                time.sleep(0.1) # Prevent Telegram flood limits
            except: pass
        bot.reply_to(m, f"✅ Broadcast complete. Sent to {success} users.")

# --- 🖼️ PHOTO HANDLER (For Vision & Covers) ---
@bot.message_handler(content_types=['photo'])
def handle_photos(m):
    if not db.is_registered(m.from_user.id): return
    mid = animator.play(m.chat.id, "Downloading to Mainframe", "matrix", speed=0.3)
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        path = f"cache_img_{m.from_user.id}.jpg"
        with open(path, "wb") as f: 
            f.write(img_data)
        
        if m.from_user.id not in user_sessions: 
            user_sessions[m.from_user.id] = {}
        user_sessions[m.from_user.id]["cover_img"] = path
        
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "📸 **Image Secured in RAM!**\nUse `👁️ Vision Analysis` to explain it, or `📕 Color PDF` to use it as a book cover.")
    except Exception as e: 
        logger.error(f"Photo save error: {e}")
        bot.reply_to(m, "⚠️ Error processing image.")

# --- 🎛️ INLINE CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda c: c.data.startswith('ai_'))
def handle_callbacks(c):
    engine = c.data.split('_')[1]
    db.update_engine(c.from_user.id, engine)
    bot.answer_callback_query(c.id, f"✅ Core Switched to {engine.upper()}")
    bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=control_panel_menu(c.from_user.id))

# --- 🏘️ MASSIVE GROUP & TEXT ROUTER ---
@bot.message_handler(func=lambda m: True)
def main_router(m):
    uid = m.from_user.id
    txt = m.text

    # 1. Registration Filter
    if uid in user_sessions and user_sessions[uid].get('reg_state') in ['edu', 'city', 'purpose']:
        return process_registration(m)
    if not db.is_registered(uid):
        return bot.reply_to(m, "⚠️ System Locked. Type /start to register first.")

    # 2. Community Group Monitor Logging (Background learning)
    if m.chat.type in ['group', 'supergroup', 'channel']:
        # If someone explicitly tags MI AI or Muaaz
        if "mi ai" in txt.lower() or "muaaz" in txt.lower():
            ans, node = mega_ai_brain(uid, f"Analyze this group chat message and reply appropriately, be helpful: {txt}")
            db.log_group_activity(m.chat.id, m.chat.title, uid, m.from_user.username, txt, ans)
            bot.reply_to(m, f"🤖 **MI AI Community Agent:**\n\n{ans}\n*(Node: {node})*")
        else:
            # Silent logging for data archiving
            db.log_group_activity(m.chat.id, m.chat.title, uid, m.from_user.username, txt)
        return

    # 3. Dashboard Command Routing
    if "⚙️ Control Panel" in txt:
        bot.send_message(m.chat.id, "🎛️ **CONTROL PANEL ONLINE**\nSelect your AI Core Engine for text processing:", reply_markup=control_panel_menu(uid))

    elif "📊 My Profile" in txt:
        u = db.get_user(uid)
        dash = (f"📊 **ENTERPRISE PROFILE** 📊\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Name: `{u[1]}`\n"
                f"🎓 Education: `{u[3]}`\n"
                f"🏙️ City: `{u[4]}`\n"
                f"🧠 Active Engine: `{u[7].upper()}`\n"
                f"⚡ Total Queries: `{u[9]}`\n"
                f"📅 Joined: `{u[10][:10]}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Level up by using the bot more!")
        bot.reply_to(m, dash, parse_mode="Markdown")

    elif "💻 Mega Code Lab" in txt:
        msg = bot.send_message(m.chat.id, "💻 **CODE LAB ACTIVE.** Enter your project requirements:")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "code"))

    elif "📦 ZIP Architect" in txt:
        msg = bot.send_message(m.chat.id, "📦 **ZIP BUILDER ACTIVE.** Tell me what full Python/Web project to build:")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "zip"))

    elif "📕 Color PDF Book" in txt:
        msg = bot.send_message(m.chat.id, "📕 **PDF ENGINE ACTIVE.** Enter the topic of the book:")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "pdf"))

    elif "🌐 Live Web Search" in txt:
        msg = bot.send_message(m.chat.id, "🌐 **WEB RADAR ONLINE.** What topic should I search on DuckDuckGo?")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "search"))

    elif "🎨 HF Art Studio" in txt:
        msg = bot.send_message(m.chat.id, "🎨 **FLUX STUDIO ONLINE.** Describe the image you want to generate:")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "art"))
        
    elif "🎥 Video & Media" in txt:
        msg = bot.send_message(m.chat.id, "🎥 **VIDEO MODULE.** Enter a topic to search for videos on the web:")
        bot.register_next_step_handler(msg, lambda m: _process_complex(m, "video"))

    elif "👁️ Vision Analysis" in txt:
        img_path = user_sessions.get(uid, {}).get("cover_img")
        if img_path and os.path.exists(img_path):
            mid = animator.play(m.chat.id, "Scanning Pixels via Gemini", "radar")
            ans, node = mega_ai_brain(uid, "Explain everything in this image in extreme detail.", img_path=img_path)
            bot.delete_message(m.chat.id, mid)
            send_long_text(m.chat.id, f"👁️ **VISION REPORT**\n━━━━━━━━━━━━━━\n{ans}\n\n`Node: {node}`")
        else: 
            bot.reply_to(m, "⚠️ Send an image first, then click this button.")

    else:
        # Standard Chat Engine Route
        mid = animator.play(m.chat.id, "Processing Neural Logic", "blocks", speed=0.3)
        ans, node = mega_ai_brain(uid, txt)
        bot.delete_message(m.chat.id, mid)
        send_long_text(m.chat.id, f"🧠 **MI AI RESPONSE**\n━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Engine:* `{node}`")

# --- UTILITY: Safe Long Text Sender ---
def send_long_text(chat_id, text):
    """Splits and sends text safely bypassing 4096 char limits"""
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            bot.send_message(chat_id, text[x:x+4000], parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown")

# --- COMPLEX HEAVY-LIFTING HANDLERS ---
def _process_complex(m, task_type):
    uid = m.from_user.id
    
    # Custom animations based on task
    anim_key = "hack" if task_type in ["code", "zip"] else ("radar" if task_type == "search" else "video")
    if task_type in ["pdf", "art"]: anim_key = "matrix"
    
    mid = animator.play(m.chat.id, f"Executing {task_type.upper()} protocol", anim_key, loops=2)
    
    try:
        if task_type == "code":
            ans, node = mega_ai_brain(uid, f"Write extensive code and explanations for: {m.text}", "Senior Programmer")
            send_long_text(m.chat.id, f"💻 **CODE LAB**\n{ans}\n`Node: {node}`")
            
        elif task_type == "zip":
            z_buf = zip_project_builder(uid, m.text)
            safe_name = re.sub(r'\W+', '_', m.text[:10])
            z_buf.name = f"MI_Project_{safe_name}.zip"
            bot.send_document(m.chat.id, z_buf, caption=f"📦 **ZIP Architecture Complete!**\nTopic: {m.text}")
            
        elif task_type == "pdf":
            img = user_sessions.get(uid, {}).get("cover_img")
            p_buf = build_color_pdf(uid, m.text, img)
            safe_name = re.sub(r'\W+', '_', m.text[:10])
            p_buf.name = f"MI_Book_{safe_name}.pdf"
            bot.send_document(m.chat.id, p_buf, caption=f"📕 **Professional PDF Published!**\nTopic: {m.text}")
            
        elif task_type == "search":
            ans, node = real_web_search(uid, m.text, mode="text")
            send_long_text(m.chat.id, f"🌐 **LIVE SEARCH REPORT**\n━━━━━━━━━━━━━━\n{ans}\n\n`Node: {node}`")
            
        elif task_type == "video":
            ans, node = real_web_search(uid, m.text, mode="video")
            send_long_text(m.chat.id, f"🎥 **VIDEO SEARCH RESULTS**\n━━━━━━━━━━━━━━\n{ans}\n\n`Node: {node}`")
            
        elif task_type == "art":
            img_path = generate_hf_image(uid, m.text)
            if img_path: 
                bot.send_photo(m.chat.id, open(img_path, 'rb'), caption=f"🎨 **Prompt:** {m.text}\n*Generated by HF FLUX*")
                # optional cleanup
                # os.remove(img_path) 
            else: 
                bot.reply_to(m, "⚠️ HF Image Engine busy or prompt rejected. Try again later.")
            
    except Exception as e: 
        logger.error(f"Complex Task Error [{task_type}]: {e}")
        bot.reply_to(m, f"⚠️ An error occurred during {task_type}. The AI node might have crashed. Check logs.")
    finally: 
        bot.delete_message(m.chat.id, mid)

# ================= 🚀 SERVER BOOT SEQUENCE =================
if __name__ == "__main__":
    print("\n" + "═"*70)
    print("🔥 MI AI MEGA ENTERPRISE EDITION V12.0 IS ONLINE 🔥")
    print("👨‍💻 Architect: Muaaz Iqbal | Organization: Muslim Islam")
    print("🌐 Modules Loaded:")
    print("   ✅ Advanced SQLite Database Engine")
    print("   ✅ Multi-Step User Registration")
    print("   ✅ Live DuckDuckGo Web & Video Search")
    print("   ✅ Multi-Node AI (Gemini, Groq, OpenRouter, HF Mistral)")
    print("   ✅ Media Generation (FLUX Art, Color PDF, ZIP Builder)")
    print("   ✅ Advanced Admin Broadcast & Community Logs")
    print("═"*70 + "\n")
    
    # Robust Keep-Alive Loop
    while True:
        try: 
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except Exception as e:
            logger.error(f"Critical Polling Crash: {e}. Auto-Rebooting in 5 seconds...")
            time.sleep(5)
