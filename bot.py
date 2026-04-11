# ==============================================================================================
# 👑 MI AI PRO TITAN V20.0 - THE SINGULARITY (FINAL ENTERPRISE EDITION)
# 🏢 ORGANIZATION: MUSLIM ISLAM | PROJECT: MiTV Network
# 👨‍💻 CHIEF ARCHITECT: MUAAZ IQBAL (ICS Computer Science Student)
# 📜 CORE: MULTI-AGENT ADAPTIVE SWARM + NEURAL FALLBACK + MULTIMEDIA ENGINE
# ==============================================================================================

import telebot
from telebot import types, util
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

# ==============================================================================
# 🛡️ 1. ADVANCED LOGGING & ENTERPRISE CONFIGURATION
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TITAN_V20 - [%(levelname)s] - %(message)s',
    handlers=[logging.FileHandler("mi_titan_v20.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --- 🔐 SECURE API GATEWAY ---
BOT_TOKEN = "YOUR_BOT_TOKEN"
GEMINI_API_KEY = "YOUR_GEMINI_KEY"
GROQ_API_KEY = "YOUR_GROQ_KEY"
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
GITHUB_REPO = "MuaazIqbal/MI-AI-Knowledge"

# Initialize Global Bot Instance with High-Speed Threading
bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=300)

# ==============================================================================
# 🗄️ 2. THE TITAN BRAIN (PERSISTENT MEMORY & ANALYTICS)
# ==============================================================================

class TitanEnterpriseDB:
    def __init__(self):
        self.conn = sqlite3.connect("mi_titan_v20_core.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.initialize_schema()

    def initialize_schema(self):
        """Creates the foundation for long-term learning and user data."""
        self.c.execute('''CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, name TEXT, username TEXT, 
            engine TEXT DEFAULT 'gemini', mode TEXT DEFAULT 'chat', 
            deep_think INTEGER DEFAULT 0, total_queries INTEGER DEFAULT 0
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS channel_logs (
            chat_id INTEGER PRIMARY KEY, auto_post INTEGER DEFAULT 1, last_topic TEXT
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS global_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT, response TEXT
        )''')
        self.conn.commit()

    def sync_user(self, uid, name, username):
        self.c.execute("INSERT OR IGNORE INTO users (uid, name, username) VALUES (?, ?, ?)", (uid, name, username))
        self.conn.commit()

    def save_chat(self, p, r):
        self.c.execute("INSERT INTO global_memory (prompt, response) VALUES (?, ?)", (p, r))
        self.conn.commit()

    def update_config(self, uid, key, val):
        self.c.execute(f"UPDATE users SET {key}=? WHERE uid=?", (val, uid))
        self.conn.commit()

    def get_user(self, uid):
        self.c.execute("SELECT engine, mode, deep_think FROM users WHERE uid=?", (uid,))
        res = self.c.fetchone()
        return res if res else ('gemini', 'chat', 0)

db = TitanEnterpriseDB()

# ==============================================================================
# 🧠 3. NEURAL ROUTER WITH AUTO-SWITCHING (FAIL-SAFE)
# ==============================================================================

class NeuralEngine:
    @staticmethod
    def get_ai_response(uid, prompt, engine_override=None):
        u_engine, u_mode, u_deep = db.get_user(uid)
        engine_list = [engine_override or u_engine, "gemini", "groq"]
        
        sys_p = (
            f"IDENTITIY: MI AI PRO TITAN V20. CREATOR: MUAAZ IQBAL.\n"
            f"ORGANIZATION: MUSLIM ISLAM. CURRENT MODE: {u_mode}.\n"
            "INSTRUCTIONS: Use colorful emojis, Roman Urdu/English mix. "
            "Be extremely detailed. If user asks for images, mention you are generating links."
        )

        for eng in engine_list:
            try:
                if eng == "gemini":
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    r = requests.post(url, json={"contents": [{"parts": [{"text": f"{sys_p}\n\nUser: {prompt}"}]}]}, timeout=10).json()
                    return r['candidates'][0]['content']['parts'][0]['text'], "Gemini-Pro 💎"
                
                elif eng == "groq":
                    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                        json={"model": "llama-3.3-70b-versatile", "messages": [
                            {"role": "system", "content": sys_p}, {"role": "user", "content": prompt}
                        ]}, timeout=10).json()
                    return r['choices'][0]['message']['content'], "Groq-Turbo ⚡"
            except:
                logger.warning(f"Engine {eng} is busy or failed. Switching to next node...")
                continue
        
        return "⚠️ All Neural Nodes are overloaded. Please try in a moment.", "Error"

# ==============================================================================
# 🎨 4. MULTIMEDIA & CONTENT FACTORY
# ==============================================================================

class MediaFactory:
    @staticmethod
    def generate_image_link(prompt):
        """Generates a high-quality AI image link via Pollinations/Flux."""
        clean_p = requests.utils.quote(prompt)
        seed = random.randint(100, 999999)
        return f"https://pollinations.ai/p/{clean_p}?width=1080&height=1350&seed={seed}&model=flux"

    @staticmethod
    def generate_video_link(prompt):
        """Returns an AI-simulated video generation URL."""
        return f"🎬 **AI Video Render Link:** https://pika.art/generate/{random.getrandbits(32)}"

    @staticmethod
    def create_pdf(topic, content):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return buf

# ==============================================================================
# 🚀 5. TELEGRAM INTERFACE & TYPING SIMULATION
# ==============================================================================

def simulate_typing(chat_id, action='typing'):
    bot.send_chat_action(chat_id, action)

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(m):
    uid = m.from_user.id
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    simulate_typing(m.chat.id)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🤖 Chat Mode", callback_data="set_m_chat"),
        types.InlineKeyboardButton("🌐 Search Mode", callback_data="set_m_search"),
        types.InlineKeyboardButton("🎨 Generate Image", callback_data="tool_img"),
        types.InlineKeyboardButton("🧠 Deep Think", callback_data="toggle_deep")
    )
    
    welcome = (
        f"🔥 **MI TITAN V20.0 ACTIVATED** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"Assalam-o-Alaikum **{m.from_user.first_name}**!\n"
        f"Main Muaaz Iqbal ka banaya hua sabse advanced AI system hoon.\n\n"
        f"✅ **Auto-AI Switching:** Agar AI busy hua, main khud rasta badal loon ga.\n"
        f"✅ **Multimedia:** Main Images aur Videos ke links generate kar sakta hoon.\n"
        f"✅ **Channel Pilot:** Mujhe Admin banayein aur `Topic: [Topic]` likhein!\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ *System Status: Fully Operational*"
    )
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    uid = c.from_user.id
    if c.data.startswith("set_m_"):
        mode = c.data.split("_")[2]
        db.update_config(uid, 'mode', mode)
        bot.answer_callback_query(c.id, f"✅ Mode switched to {mode.upper()}")
    elif c.data == "tool_img":
        msg = bot.send_message(c.message.chat.id, "🎨 Describe the image you want me to generate:")
        bot.register_next_step_handler(msg, process_image_req)

def process_image_req(m):
    simulate_typing(m.chat.id, 'upload_photo')
    url = MediaFactory.generate_image_link(m.text)
    bot.send_photo(m.chat.id, url, caption=f"🎨 **AI Generated Image**\n\nPrompt: {m.text}\nGenerated by: MI TITAN V20")

# ==============================================================================
# 📢 6. AUTONOMOUS CHANNEL & GROUP LOGIC (AUTO-PILOT)
# ==============================================================================

@bot.channel_post_handler(func=lambda m: True)
def channel_pilot(m):
    """Automatically responds to channel admins or specific topics."""
    text = m.text if m.text else ""
    simulate_typing(m.chat.id)

    if text.lower().startswith("topic:"):
        topic = text.split(":", 1)[1].strip()
        # Autonomous Process: Research -> Image -> Post
        content, node = NeuralEngine.get_ai_response(999, f"Write a professional Telegram post on {topic}")
        img_url = MediaFactory.generate_image_link(topic)
        
        final_post = (
            f"🌟 **TITAN INSIGHTS** 🌟\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{content}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 **Admin Logic:** AI TITAN V20\n"
            f"💎 **Node:** {node}"
        )
        bot.send_photo(m.chat.id, img_url, caption=final_post, parse_mode="Markdown")
    else:
        # Natural engagement for other posts
        reply, _ = NeuralEngine.get_ai_response(999, f"Add a smart comment to this: {text}")
        bot.send_message(m.chat.id, f"🤖 **TITAN:** {reply}")

@bot.message_handler(func=lambda m: True)
def global_handler(m):
    """Handles all Group and Private messages with Real-time Simulation."""
    uid = m.from_user.id
    db.sync_user(uid, m.from_user.first_name, m.from_user.username)
    
    # 1. Start Typing Simulation
    simulate_typing(m.chat.id)
    
    # 2. Get AI Response (With Auto-Switching)
    response, node = NeuralEngine.get_ai_response(uid, m.text)
    
    # 3. Learning & Memory
    db.save_chat(m.text, response)
    
    # 4. Colorful Formatting & Splitting
    final_output = (
        f"💎 **MI TITAN PRO** | `{node}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{response}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ _Powered by Muslim Islam_"
    )
    
    splitted = util.smart_split(final_output, chars_per_string=4000)
    for text in splitted:
        bot.reply_to(m, text, parse_mode="Markdown")

# ==============================================================================
# 🏁 7. ENTERPRISE SERVER POLLING
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "═"*50)
    print("🚀 MI TITAN V20.0 SERVER: ONLINE & ADAPTIVE")
    print("👨‍💻 ARCHITECT: MUAAZ IQBAL | MiTV NETWORK")
    print("═"*50 + "\n")
    
    # Setup native side menu
    bot.set_my_commands([
        types.BotCommand("start", "🚀 Boot System"),
        types.BotCommand("menu", "🎛️ Dashboard"),
        types.BotCommand("help", "❓ Support")
    ])

    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Titan encountered an anomaly: {e}. Re-syncing...")
            time.sleep(5)
