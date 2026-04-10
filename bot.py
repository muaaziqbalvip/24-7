# ==============================================================================
# 👑 MI AI PRO SUPREME - THE BOMB EDITION (ENTERPRISE MASTER SCRIPT)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 📍 LOCATION: KASUR, PUNJAB, PAKISTAN
# ==============================================================================
# DESCRIPTION: A massive, all-in-one AI ecosystem featuring Multi-Model AI routing,
# persistent SQLite memory, dynamic PDF/ZIP generation, Google Sync, and deep logic.
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
from fpdf import FPDF
from datetime import datetime
import logging
import traceback

# --- ⚙️ CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MI AI CORE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")
GROQ_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY_HERE")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY_HERE")

# --- 🎨 ENTERPRISE THEMES & TEMPLATES ---
UI_THEMES = {
    "progress_bars": {
        "red": ["🟥⬜⬜⬜⬜ 20%", "🟥🟥⬜⬜⬜ 40%", "🟥🟥🟥⬜⬜ 60%", "🟥🟥🟥🟥⬜ 80%", "🟩🟩🟩🟩🟩 100%"],
        "blue": ["🟦⬜⬜⬜⬜ 20%", "🟦🟦⬜⬜⬜ 40%", "🟦🟦🟦⬜⬜ 60%", "🟦🟦🟦🟦⬜ 80%", "🟩🟩🟩🟩🟩 100%"]
    },
    "messages": {
        "welcome": "🌟 **MI AI SUPREME INITIATED** 🌟\n\nMaster {}, your enterprise ecosystem is online.",
        "error": "⚠️ **System Overload:** AI node failed to respond. Retrying..."
    }
}

# ==============================================================================
# 🗄️ COMPONENT 1: ADVANCED DATABASE SYSTEM (SQLITE)
# ==============================================================================
class MI_DatabaseSystem:
    def __init__(self, db_name='mi_ai_enterprise.db'):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.c = self.conn.cursor()
            self.c.execute('''CREATE TABLE IF NOT EXISTS users 
                              (uid INTEGER PRIMARY KEY, name TEXT, engine TEXT, 
                               role TEXT, queries INTEGER, joined_date TEXT)''')
            self.c.execute('''CREATE TABLE IF NOT EXISTS memory 
                              (uid INTEGER, role TEXT, content TEXT, timestamp TEXT)''')
            self.conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database Error: {e}")

    def register_user(self, uid, name):
        try:
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.c.execute("INSERT OR IGNORE INTO users (uid, name, engine, role, queries, joined_date) VALUES (?, ?, 'groq', 'Standard', 0, ?)", (uid, name, date_now))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Registration Error: {e}")

    def get_user_profile(self, uid):
        self.c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        return self.c.fetchone()

    def update_setting(self, uid, column, value):
        query = f"UPDATE users SET {column}=? WHERE uid=?"
        self.c.execute(query, (value, uid))
        self.conn.commit()

    def add_query_count(self, uid):
        self.c.execute("UPDATE users SET queries = queries + 1 WHERE uid=?", (uid,))
        self.conn.commit()

# ==============================================================================
# 🧠 COMPONENT 2: MULTI-NODE AI ROUTER
# ==============================================================================
class MI_AI_Router:
    def __init__(self):
        self.session = requests.Session()

    def generate_response(self, uid, prompt, sys_role="Senior Full-Stack Developer", memory_context=""):
        user_data = db.get_user_profile(uid)
        if not user_data:
            return "User not registered.", "Error"
        
        engine = user_data[2]
        full_prompt = f"System Protocol: Your name is MI AI. Creator: Muaaz Iqbal. Role: {sys_role}.\nContext:\n{memory_context}\n\nUser Request: {prompt}"
        
        if engine == "groq":
            return self._call_groq(full_prompt)
        elif engine == "openrouter":
            return self._call_openrouter(full_prompt)
        else:
            return self._call_gemini(full_prompt)

    def _call_groq(self, prompt):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
        try:
            r = self.session.post(url, headers=headers, json=payload, timeout=25)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'], "Groq-70B ⚡"
        except Exception as e:
            logger.error(f"Groq failed: {e}")
            return self._call_gemini(prompt) # Fallback

    def _call_gemini(self, prompt):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = self.session.post(url, json=payload, timeout=25)
            r.raise_for_status()
            return r.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini-Pro 💎"
        except Exception as e:
            logger.error(f"Gemini failed: {e}")
            return "All AI cores are currently experiencing heavy load. Please try again.", "Offline"

    def _call_openrouter(self, prompt):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
        payload = {"model": "openai/gpt-4-turbo", "messages": [{"role": "user", "content": prompt}]}
        try:
            r = self.session.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'], "OpenRouter 🌌"
        except:
            return self._call_groq(prompt)

# ==============================================================================
# 📦 COMPONENT 3: ARCHITECTURE BUILDERS (ZIP & PDF)
# ==============================================================================
class MI_FileArchitect:
    @staticmethod
    def create_zip_project(raw_ai_code, project_name):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            try:
                # Parsing complex AI output looking for FILE: and CODE: markers
                sections = raw_ai_code.split("FILE:")
                for sec in sections[1:]:
                    lines = sec.strip().split("\n")
                    filename = lines[0].replace("CODE:", "").strip()
                    content = "\n".join(lines[1:]).replace("```python", "").replace("```html", "").replace("```", "").strip()
                    z.writestr(filename, content)
                
                # Adding standard organizational files
                z.writestr("MI_README.md", f"# {project_name}\n\nBuilt by MI AI PRO SUPREME.\nArchitect: Muaaz Iqbal.\nOrganization: Muslim Islam.")
            except Exception as e:
                logger.error(f"ZIP Parsing Error: {e}")
                z.writestr("fallback_code.txt", raw_ai_code)
        buf.seek(0)
        return buf

    @staticmethod
    def create_luxury_pdf(topic, content, cover_img_path=None):
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- COVER PAGE ---
        pdf.add_page()
        pdf.set_fill_color(139, 0, 0) # Dark Red Luxury
        pdf.rect(0, 0, 210, 297, 'F')
        
        if cover_img_path and os.path.exists(cover_img_path):
            try:
                pdf.image(cover_img_path, x=15, y=40, w=180)
            except: pass
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 32)
        pdf.set_xy(10, 180)
        pdf.multi_cell(190, 15, topic.upper(), align='C')
        
        pdf.set_font("Arial", 'I', 16)
        pdf.set_xy(10, 250)
        pdf.cell(190, 10, "A Comprehensive Report by MI AI", ln=True, align='C')
        pdf.cell(190, 10, "Master: Muaaz Iqbal", ln=True, align='C')

        # --- CONTENT PAGES ---
        pdf.add_page()
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Arial", size=12)
        
        # Clean text for FPDF latin-1 limitation
        clean_content = content.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, clean_content)
        
        # --- FOOTER LOGIC ---
        # FPDF doesn't support direct dynamic footers without subclassing, doing manual here
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(128)
        pdf.cell(0, 10, 'MI AI PRO SUPREME - Muslim Islam', 0, 0, 'C')

        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return buf

# ==============================================================================
# 🤖 COMPONENT 4: BOT INITIALIZATION & UI
# ==============================================================================
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=5)
db = MI_DatabaseSystem()
ai_core = MI_AI_Router()
architect = MI_FileArchitect()

user_sessions = {}

def get_supreme_dashboard():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    m.add("📊 Control Panel", "🧠 Supreme Chat", "💻 Architect ZIP")
    m.add("🖼️ Visual Engine", "🌐 Deep Scan Sync", "🎬 Render Video")
    m.add("📕 Create Luxury Book", "⚙️ Hardware Switch", "📖 Story Mode")
    return m

def animate_progress(chat_id, task):
    msg = bot.send_message(chat_id, f"🔴 **Initiating: {task}**", parse_mode="Markdown")
    for bar in UI_THEMES["progress_bars"]["red"]:
        try:
            text = f"🔥 **MI AI SUPREME CORE**\n━━━━━━━━━━━━━━━━━\n⚙️ `{task}`\n📊 {bar}\n👨‍💻 *Architect: Muaaz Iqbal*"
            bot.edit_message_text(text, chat_id, msg.message_id, parse_mode="Markdown")
            time.sleep(0.6)
        except: pass
    return msg.message_id

# ==============================================================================
# 📡 COMPONENT 5: ROUTING & LOGIC HANDLERS
# ==============================================================================
@bot.message_handler(commands=['start', 'help'])
def boot_sequence(m):
    db.register_user(m.from_user.id, m.from_user.first_name)
    user_sessions[m.from_user.id] = {"cover": None, "state": "idle"}
    bot.send_message(m.chat.id, UI_THEMES["messages"]["welcome"].format(m.from_user.first_name), 
                     parse_mode="Markdown", reply_markup=get_supreme_dashboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith('sw_'))
def handle_engine_switch(c):
    engine = c.data.split('_')[1]
    db.update_setting(c.from_user.id, "engine", engine)
    bot.answer_callback_query(c.id, f"Core Switched to {engine.upper()}")
    bot.edit_message_text(f"⚙️ **System Override:** Core Engine set to **{engine.upper()}**.", c.message.chat.id, c.message.message_id)

@bot.message_handler(content_types=['photo'])
def handle_image_input(m):
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        path = f"temp_{m.from_user.id}.jpg"
        with open(path, "wb") as f: f.write(img_data)
        
        if m.from_user.id not in user_sessions: user_sessions[m.from_user.id] = {}
        user_sessions[m.from_user.id]["cover"] = path
        bot.reply_to(m, "📸 **Visual Data Stored.**\nThis will be used as a cover for your next Luxury Book, or you can ask me to analyze it.")
    except Exception as e:
        logger.error(f"Image Error: {e}")
        bot.reply_to(m, "⚠️ Image processing failed.")

@bot.message_handler(func=lambda m: True)
def central_router(m):
    uid = m.from_user.id
    txt = m.text
    db.add_query_count(uid)

    if txt == "⚙️ Hardware Switch":
        m_inline = types.InlineKeyboardMarkup()
        m_inline.add(types.InlineKeyboardButton("⚡ Groq 70B Core", callback_data="sw_groq"))
        m_inline.add(types.InlineKeyboardButton("💎 Gemini Logic Core", callback_data="sw_gemini"))
        m_inline.add(types.InlineKeyboardButton("🌌 OpenRouter API", callback_data="sw_openrouter"))
        bot.send_message(m.chat.id, "🎛️ **Hardware Configuration:**", reply_markup=m_inline)

    elif txt == "📊 Control Panel":
        u = db.get_user_profile(uid)
        bot.reply_to(m, f"📊 **System Status:**\nUser: {u[1]}\nActive Core: {u[2].upper()}\nTotal Tasks: {u[4]}\nAccess Level: SUPREME 👑")

    elif txt == "💻 Architect ZIP":
        msg = bot.send_message(m.chat.id, "💻 **Enter full project architecture requirements:**\n*(I will write long code and create a ZIP structure)*")
        bot.register_next_step_handler(msg, execute_zip_task)

    elif txt == "📕 Create Luxury Book":
        msg = bot.send_message(m.chat.id, "📕 **Enter the Book Topic:**\n*(Send a photo beforehand if you want a custom cover)*")
        bot.register_next_step_handler(msg, execute_pdf_task)

    elif txt == "🌐 Deep Scan Sync":
        msg = bot.send_message(m.chat.id, "🌐 **What topic should I deep scan on Google?**")
        bot.register_next_step_handler(msg, execute_search_task)
        
    elif txt == "🖼️ Visual Engine":
        msg = bot.send_message(m.chat.id, "🎨 **Describe the art you want me to generate:**")
        bot.register_next_step_handler(msg, execute_art_task)

    else:
        # Standard Deep Chat
        mid = animate_progress(m.chat.id, "Analyzing Deep Logic")
        ans, engine_name = ai_core.generate_response(uid, txt)
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"🔴 **MI AI SUPREME:**\n━━━━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Powered by {engine_name}*", parse_mode="Markdown")

# --- 🚀 EXECUTION FUNCTIONS ---
def execute_zip_task(m):
    mid = animate_progress(m.chat.id, "Compiling ZIP Architecture")
    prompt = f"Act as Senior Architect. Write long, complete code for: {m.text}. Use the format:\nFILE: filename.ext\nCODE:\n[your code here]\nDo this for all necessary files."
    raw_code, _ = ai_core.generate_response(m.from_user.id, prompt, "Senior Software Architect")
    
    zip_buffer = architect.create_zip_project(raw_code, m.text[:20])
    zip_buffer.name = "MI_Project_Supreme.zip"
    
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, zip_buffer, caption=f"📦 **Project Compiled Successfully.**\nTask: {m.text}")

def execute_pdf_task(m):
    mid = animate_progress(m.chat.id, "Publishing Luxury Book")
    topic = m.text
    content, _ = ai_core.generate_response(m.from_user.id, f"Write a massive, multi-chapter detailed book on '{topic}'. Include headings, deep research, and index.", "Expert Author")
    
    cover_path = user_sessions.get(m.from_user.id, {}).get("cover")
    pdf_buffer = architect.create_luxury_pdf(topic, content, cover_path)
    pdf_buffer.name = f"{topic[:20]}.pdf"
    
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, pdf_buffer, caption=f"📕 **Luxury Edition Published!**\nTopic: {topic}")
    
    # Cleanup cover image
    if cover_path and os.path.exists(cover_path):
        os.remove(cover_path)
        user_sessions[m.from_user.id]["cover"] = None

def execute_search_task(m):
    mid = animate_progress(m.chat.id, "Syncing with Google Servers")
    query = m.text
    
    # Fetch lookalike image and deep text report
    img_url = f"https://pollinations.ai/p/{urllib.parse.quote(query)}?width=800&height=400&nologo=true"
    report, engine = ai_core.generate_response(m.from_user.id, f"Search internet and provide a highly detailed, professional report on: {query}", "Web Researcher")
    
    bot.delete_message(m.chat.id, mid)
    bot.send_photo(m.chat.id, img_url, caption=f"🌐 **Deep Scan Complete ({engine}):**\n\n{report[:800]}...\n\n🔗 [View Full Live Results](https://www.google.com/search?q={urllib.parse.quote(query)})")

def execute_art_task(m):
    p = urllib.parse.quote(m.text)
    bot.send_photo(m.chat.id, f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){p}?nologo=true", caption=f"🎨 Visual Created for: {m.text}")

# ==============================================================================
# 🚀 SYSTEM BOOTLOADER
# ==============================================================================
if __name__ == "__main__":
    logger.info("========================================")
    logger.info("🔥 MI AI SUPREME EDITION ONLINE 🔥")
    logger.info("👨‍💻 Architect: Muaaz Iqbal | Muslim Islam")
    logger.info("========================================")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=15)
    except Exception as e:
        logger.error(f"Bot Crashed: {e}")
        time.sleep(10)
