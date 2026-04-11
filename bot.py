# ==============================================================================================
# 👑 MI AI PRO TITAN V18.0 - THE ENTERPRISE AUTONOMOUS AGENT
# 🏢 ORGANIZATION: MUSLIM ISLAM | PROJECT: MiTV Network
# 👨‍💻 CHIEF ARCHITECT: MUAAZ IQBAL (ICS Computer Science Student)
# 📜 DESCRIPTION: Multi-Model AI with Autonomous Image Fetching, Channel Management, 
#                 GitHub Sync, PDF/ZIP Tools, and Multi-Agent Swarm Intelligence.
# ==============================================================================================

import telebot
from telebot import types
import requests
import os
import time
import json
import base64
import threading
import sqlite3
import logging
import random
import re
import io
import zipfile
import shutil
from datetime import datetime
from fpdf import FPDF
from duckduckgo_search import DDGS
from PIL import Image
from functools import wraps

# ==============================================================================
# 🛡️ 1. SYSTEM LOGGING & GLOBAL CONFIGURATION
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TITAN_V18 - [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("mi_titan_v18.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 🔐 SECURE API KEYS (Environment Variables Recommended) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MuaazIqbal/MI-AI-Knowledge-Base")

# --- ⚙️ BOT INITIALIZATION ---
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=250)

# ==============================================================================
# 🗄️ 2. TITAN ENTERPRISE DATABASE ARCHITECTURE
# ==============================================================================

class TitanEnterpriseDB:
    def __init__(self):
        self.db_path = "mi_titan_enterprise_v18.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialize_schema()

    def initialize_schema(self):
        """Creates the foundation for user data, channel configs, and logs."""
        # User Management Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, 
            name TEXT, 
            username TEXT, 
            engine TEXT DEFAULT 'gemini', 
            mode TEXT DEFAULT 'chat', 
            deep_think INTEGER DEFAULT 0, 
            is_admin INTEGER DEFAULT 0,
            queries_count INTEGER DEFAULT 0,
            joined_at TEXT
        )''')
        
        # Channel/Group Monitoring Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ecosystem (
            chat_id INTEGER PRIMARY KEY, 
            type TEXT, 
            title TEXT, 
            auto_post INTEGER DEFAULT 1, 
            last_activity TEXT
        )''')
        
        # Knowledge Repository Logs
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            topic TEXT, 
            summary TEXT, 
            github_url TEXT, 
            timestamp TEXT
        )''')
        
        self.conn.commit()
        logger.info("Enterprise Database Schema Verified.")

    # --- User Methods ---
    def sync_user(self, uid, name, username):
        self.cursor.execute("SELECT uid FROM users WHERE uid=?", (uid,))
        if not self.cursor.fetchone():
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''INSERT INTO users (uid, name, username, joined_at) 
                                 VALUES (?, ?, ?, ?)''', (uid, name, username, date_now))
            self.conn.commit()

    def get_config(self, uid):
        self.cursor.execute("SELECT engine, mode, deep_think, is_admin FROM users WHERE uid=?", (uid,))
        res = self.cursor.fetchone()
        return {"engine": res[0], "mode": res[1], "deep_think": res[2], "is_admin": res[3]} if res else None

    def update_val(self, uid, column, value):
        self.cursor.execute(f"UPDATE users SET {column}=? WHERE uid=?", (value, uid))
        self.conn.commit()

    # --- Ecosystem Methods ---
    def register_chat(self, chat_id, chat_type, title):
        self.cursor.execute("INSERT OR IGNORE INTO ecosystem (chat_id, type, title) VALUES (?, ?, ?)", 
                           (chat_id, chat_type, title))
        self.conn.commit()

db = TitanEnterpriseDB()

# ==============================================================================
# 🧠 3. ADVANCED NEURAL ROUTING ENGINE
# ==============================================================================

class AIAgentSwarm:
    """Handles multiple AI nodes for high-availability research."""
    
    @staticmethod
    def get_system_prompt(uid, role="General Intelligence"):
        u = db.get_config(uid)
        base = (
            f"IDENTITIY: MI AI PRO TITAN V18. CREATED BY: MUAAZ IQBAL.\n"
            f"ORGANIZATION: MUSLIM ISLAM. MISSION: EDUCATE AND EMPOWER.\n"
            f"ROLE: {role}. LANGUAGE: Roman Urdu + English (Mix).\n"
            "INSTRUCTIONS: Be respectful, extremely detailed, and use emojis. "
            "Never provide short answers. Explain the logic behind everything."
        )
        if u and u['deep_think']:
            base += "\n[MODE: DEEP THINK]: Breakdown every problem step-by-step with high logic."
        return base

    @staticmethod
    def call_node(uid, prompt, engine=None, image_b64=None, role="Expert"):
        u = db.get_config(uid)
        target_engine = engine or (u['engine'] if u else 'gemini')
        sys_p = AIAgentSwarm.get_system_prompt(uid, role)

        # Vision Logic (Always Gemini Pro)
        if image_b64:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": f"System: {sys_p}\nUser: {prompt}"}, {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}]}]}
            try:
                r = requests.post(url, json=payload, timeout=30).json()
                return r['candidates'][0]['content']['parts'][0]['text'], "Gemini Vision"
            except: return "⚠️ Vision Node Offline.", "Error"

        # Text Logic with Multi-Node Fallback
        if target_engine == "groq":
            try:
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                                 json={"model": "llama-3.3-70b-versatile", "messages": [
                                     {"role": "system", "content": sys_p}, {"role": "user", "content": prompt}
                                 ]}, timeout=15).json()
                return r['choices'][0]['message']['content'], "Groq (Llama 3.3)"
            except: target_engine = "gemini" # Fallback

        if target_engine == "gemini":
            try:
                model = "gemini-1.5-pro" if (u and u['deep_think']) else "gemini-1.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
                r = requests.post(url, json={"contents": [{"parts": [{"text": f"System: {sys_p}\nUser: {prompt}"}]}]}).json()
                return r['candidates'][0]['content']['parts'][0]['text'], f"Google ({model})"
            except: return "⚠️ Critical: All Neural Nodes are unresponsive.", "System Error"

# ==============================================================================
# 🖼️ 4. AUTONOMOUS ASSET FETCHING (IMAGE ENGINE)
# ==============================================================================

class AssetManager:
    """Searches, downloads, and processes images from the web."""
    
    @staticmethod
    def fetch_image(topic):
        logger.info(f"Searching image for: {topic}")
        try:
            with DDGS() as ddgs:
                # Optimized search query
                search_query = f"{topic} professional wallpaper high quality"
                results = [r for r in ddgs.images(search_query, max_results=10)]
                
                if not results: return None
                
                # Pick a random high-quality image from top results
                img_url = random.choice(results[:5])['image']
                response = requests.get(img_url, timeout=20, stream=True)
                
                if response.status_code == 200:
                    filename = f"asset_{random.randint(1000, 9999)}.jpg"
                    with open(filename, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    
                    # Optional: Verify with Pillow
                    with Image.open(filename) as img:
                        img.verify()
                    return filename
        except Exception as e:
            logger.error(f"Image Fetch Failure: {e}")
        return None

# ==============================================================================
# 🐙 5. KNOWLEDGE SYNC (GITHUB INTEGRATION)
# ==============================================================================

def push_to_github(topic, content):
    """Syncs research data to GitHub repository for long-term storage."""
    if GITHUB_TOKEN == "YOUR_GITHUB_TOKEN": return None
    
    clean_topic = re.sub(r'\W+', '_', topic.lower()[:30])
    file_path = f"research/MI_TITAN_{clean_topic}.md"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        # Check if file exists
        res = requests.get(url, headers=headers)
        sha = res.json().get('sha') if res.status_code == 200 else None
        
        md_text = f"# MI AI Knowledge Base\n\n**Topic:** {topic}\n**Generated:** {datetime.now()}\n\n{content}\n\n---\n*Created by Muaaz Iqbal's TITAN V18*"
        b64_content = base64.b64encode(md_text.encode()).decode()
        
        payload = {"message": f"🤖 Knowledge Log: {topic}", "content": b64_content}
        if sha: payload["sha"] = sha
        
        put_res = requests.put(url, headers=headers, json=payload)
        return f"https://github.com/{GITHUB_REPO}/blob/main/{file_path}" if put_res.status_code in [200, 201] else None
    except Exception as e:
        logger.error(f"GitHub Sync Error: {e}")
        return None

# ==============================================================================
# 📢 6. AUTONOMOUS CHANNEL PILOT (THE CORE REQUEST)
# ==============================================================================

def run_autonomous_post(chat_id, topic, admin_name, uid):
    """Full Cycle: Research -> Image -> Formatting -> Posting"""
    status_msg = bot.send_message(chat_id, f"🚀 **MI TITAN AUTO-PILOT INITIATED**\n\nAdmin `{admin_name}` ne topic diya hai: **{topic}**\nBhai, thora sabr karein, main data aur image nikaal raha hoon...")

    # 1. Deep Research
    bot.edit_message_text(f"🔍 **Step 1:** Researching '{topic}' using Neural Nodes...", chat_id, status_msg.message_id)
    research_prompt = f"Write a professional, viral, and highly informative Telegram post about {topic}. Use headings, emojis, and a call to action at the end."
    content, engine = AIAgentSwarm.call_node(uid, research_prompt, role="Content Specialist")

    # 2. Image Fetching
    bot.edit_message_text(f"🖼️ **Step 2:** Searching and downloading relevant image for '{topic}'...", chat_id, status_msg.message_id)
    img_path = AssetManager.fetch_image(topic)

    # 3. GitHub Sync
    bot.edit_message_text(f"🐙 **Step 3:** Syncing knowledge to GitHub Knowledge Base...", chat_id, status_msg.message_id)
    github_link = push_to_github(topic, content)
    sync_status = f"\n\n📂 [View in GitHub Knowledge Base]({github_link})" if github_link else ""

    # 4. Final Post
    final_caption = (
        f"🌟 **MI TITAN EXCLUSIVE POST** 🌟\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{content}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 **Admin:** {admin_name}\n"
        f"🤖 **Node:** {engine}\n"
        f"🏢 **Organization:** Muslim Islam{sync_status}"
    )

    bot.delete_message(chat_id, status_msg.message_id)
    
    if img_path:
        with open(img_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=final_caption, parse_mode="Markdown")
        os.remove(img_path)
    else:
        bot.send_message(chat_id, final_caption, parse_mode="Markdown")

# ==============================================================================
# 🎛️ 7. UI & UX ARCHITECTURE (DIGITAL KEYBOARDS)
# ==============================================================================

def get_dashboard_markup(uid):
    u = db.get_config(uid)
    markup = types.InlineKeyboardMarkup(row_width=2)
    dt_tick = "✅" if u['deep_think'] else "❌"
    
    markup.add(
        types.InlineKeyboardButton("🤖 AI Chat", callback_data="m_chat"),
        types.InlineKeyboardButton(f"🧠 Deep Think: {dt_tick}", callback_data="t_deep")
    )
    markup.add(
        types.InlineKeyboardButton("🌐 Web Search", callback_data="m_search"),
        types.InlineKeyboardButton("👥 Agent Swarm", callback_data="t_swarm")
    )
    markup.add(
        types.InlineKeyboardButton("💻 Code Lab", callback_data="m_code"),
        types.InlineKeyboardButton("📖 Story Mode", callback_data="m_story")
    )
    markup.add(
        types.InlineKeyboardButton("📕 Generate PDF", callback_data="tool_pdf"),
        types.InlineKeyboardButton("📦 ZIP Creator", callback_data="tool_zip")
    )
    markup.add(types.InlineKeyboardButton("⚙️ Change AI Neural Engine", callback_data="menu_engine"))
    return markup

def get_engine_markup(uid):
    u = db.get_config(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    engines = [('gemini', '💎 Google Gemini Pro'), ('groq', '⚡ Groq Llama 3.3'), ('openrouter', '🌌 OpenRouter GPT-4')]
    for code, name in engines:
        tick = " ✅" if u['engine'] == code else ""
        markup.add(types.InlineKeyboardButton(f"{name}{tick}", callback_data=f"set_e_{code}"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="go_home"))
    return markup

# ==============================================================================
# 🚀 8. CORE TELEGRAM HANDLERS
# ==============================================================================

@bot.channel_post_handler(func=lambda m: True)
def channel_automation_handler(m):
    """Triggers autonomous posting when any admin writes 'Topic: XYZ'"""
    db.register_chat(m.chat.id, 'channel', m.chat.title)
    text = m.text if m.text else ""
    
    if text.lower().startswith("topic:") or text.lower().startswith("post on:"):
        topic = text.split(":", 1)[1].strip()
        threading.Thread(target=run_autonomous_post, args=(m.chat.id, topic, "Channel Admin", 999)).start()

@bot.message_handler(commands=['start', 'menu'])
def welcome_handler(m):
    uid = m.from_user.id
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    
    if m.chat.type == 'private':
        welcome_txt = (
            f"🔥 **MI AI PRO TITAN V18.0 ACTIVATED**\n\n"
            f"Assalam-o-Alaikum, **{m.from_user.first_name}**! Main Muaaz Iqbal ka banaya hua "
            f"sabse advanced autonomous AI system hoon.\n\n"
            f"**CHANNELS MEIN KAAM:**\n"
            f"Mujhe apne channel mein Admin banayein aur likhen: `Topic: Space Science`.\n"
            f"Main khud hi research karunga aur image download karke post kar dunga!\n\n"
            f"Niche diye gaye dashboard se features use karein:"
        )
        bot.send_message(m.chat.id, welcome_txt, parse_mode="Markdown", reply_markup=get_dashboard_markup(uid))
    else:
        db.register_chat(m.chat.id, m.chat.type, m.chat.title)
        bot.send_message(m.chat.id, "🤖 **TITAN V18 SYSTEM INTEGRATED.** Main is group/channel ke har message par nazar rakh raha hoon.")

@bot.callback_query_handler(func=lambda c: True)
def callback_router(c):
    uid = c.from_user.id
    d = c.data
    
    if d == "go_home":
        bot.edit_message_text("🎛️ **MI TITAN CONTROL PANEL**", c.message.chat.id, c.message.message_id, reply_markup=get_dashboard_markup(uid))
    elif d == "menu_engine":
        bot.edit_message_text("⚙️ **SELECT NEURAL ENGINE**", c.message.chat.id, c.message.message_id, reply_markup=get_engine_markup(uid))
    elif d.startswith("set_e_"):
        eng = d.split("_")[2]
        db.update_val(uid, 'engine', eng)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=get_engine_markup(uid))
    elif d == "t_deep":
        u = db.get_config(uid)
        db.update_val(uid, 'deep_think', 0 if u['deep_think'] else 1)
        bot.edit_message_reply_markup(c.message.chat.id, c.message.message_id, reply_markup=get_dashboard_markup(uid))
    elif d.startswith("m_"):
        mode = d.split("_")[1]
        db.update_val(uid, 'mode', mode)
        bot.answer_callback_query(c.id, f"✅ Mode: {mode.upper()} Activated")
    elif d == "tool_pdf":
        msg = bot.send_message(c.message.chat.id, "📕 Topic likhen jis par PDF Book banani hai:")
        bot.register_next_step_handler(msg, handle_pdf_tool)
    elif d == "tool_zip":
        msg = bot.send_message(c.message.chat.id, "📦 Code requirements likhen (ZIP banane ke liye):")
        bot.register_next_step_handler(msg, handle_zip_tool)

# --- 🛠️ TOOL HANDLERS ---
def handle_pdf_tool(m):
    topic = m.text
    mid = bot.send_message(m.chat.id, "⏳ Generating Professional PDF...").message_id
    content, _ = AIAgentSwarm.call_node(m.from_user.id, f"Detailed educational report on {topic}", role="Researcher")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    buf.name = f"MI_Report_{topic.replace(' ', '_')}.pdf"
    bot.send_document(m.chat.id, buf)
    bot.delete_message(m.chat.id, mid)

def handle_zip_tool(m):
    req = m.text
    mid = bot.send_message(m.chat.id, "⏳ Building Project Structure...").message_id
    code_raw, _ = AIAgentSwarm.call_node(m.from_user.id, f"Create a full coding project for: {req}. Use <<<FILE: name>>> tags.", role="Senior Developer")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        files = re.findall(r'<<<FILE:\s*(.+?)>>>(.*?)(?:<<<ENDFILE>>>|\Z)', code_raw, re.DOTALL)
        if files:
            for name, code in files: z.writestr(name.strip(), code.strip())
        else: z.writestr("main_logic.py", code_raw)
    
    buf.seek(0)
    buf.name = "MI_TITAN_PROJECT.zip"
    bot.send_document(m.chat.id, buf)
    bot.delete_message(m.chat.id, mid)

# --- 🌍 GLOBAL MESSAGE PROCESSOR ---
@bot.message_handler(func=lambda m: True)
def global_message_handler(m):
    uid = m.from_user.id
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    u = db.get_config(uid)
    text = m.text

    # Link Detection
    if "t.me/" in text:
        analysis, _ = AIAgentSwarm.call_node(uid, f"Analyze this Telegram link and purpose: {text}", role="Security Analyst")
        return bot.reply_to(m, f"🔍 **LINK ANALYSIS:**\n{analysis}")

    # Group Logic: Respond to everything or when mentioned
    if m.chat.type != 'private':
        ans, node = AIAgentSwarm.call_node(uid, text)
        bot.reply_to(m, f"🤖 {ans}")
    else:
        # Private Chat Logic
        status_mid = bot.reply_to(m, "⏳ *Neural processing...*").message_id
        if u['mode'] == 'search':
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(text, max_results=3)]
                context = "\n".join([f"- {r['body']}" for r in results])
                ans, node = AIAgentSwarm.call_node(uid, f"Web Data:\n{context}\n\nQuestion: {text}", role="Web Researcher")
        else:
            ans, node = AIAgentSwarm.call_node(uid, text)
        
        bot.delete_message(m.chat.id, status_mid)
        bot.send_message(m.chat.id, f"💎 **MI TITAN** | `{node}`\n━━━━━━━━━━━━━━\n\n{ans}")

# ================= 🚀 9. SERVER EXECUTION =================
if __name__ == "__main__":
    # Setup native side menu
    bot.set_my_commands([
        types.BotCommand("start", "🚀 Reset System"),
        types.BotCommand("menu", "🎛️ Open Dashboard"),
        types.BotCommand("swarm", "👥 AI Swarm Meeting")
    ])
    
    print("\n" + "═"*50)
    print("🔥 MI AI TITAN V18.0 - ENTERPRISE SERVER LIVE 🔥")
    print("👨‍💻 Chief Architect: Muaaz Iqbal")
    print("🏢 Organization: Muslim Islam")
    print("═"*50 + "\n")
    
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=90)
        except Exception as e:
            logger.error(f"Server Crash: {e}. Rebooting...")
            time.sleep(5)
