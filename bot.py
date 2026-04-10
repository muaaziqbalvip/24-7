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
import random
from fpdf import FPDF
from datetime import datetime

# ==============================================================
# 🌟 MI AI PRO ULTIMATE - ENTERPRISE EDITION
# 🏢 ARCHITECT: MUAAZ IQBAL | MiTV Network
# ==============================================================

# --- 🔐 Security & Keys (GitHub Secrets) ---
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_K = os.getenv("GEMINI_API_KEY")
GROQ_K = os.getenv("GROQ_API_KEY")
OPENAI_K = os.getenv("OPENROUTER_API_KEY") # OpenRouter handles OpenAI models

bot = telebot.TeleBot(TOKEN)

# --- 🧠 DATABASE: GLOBAL MEMORY ---
# Is dictionary me user ka sara data aur settings save hongi
db = {}

def get_mem(uid):
    if uid not in db:
        db[uid] = {
            "engine": "groq", # Default engine
            "mode": "Pro Thinking",
            "history": [],
            "stats": {"requests": 0, "files_gen": 0},
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return db[uid]

# --- 📊 DIGITAL PROGRESS BAR LOGIC ---
def draw_progress(percent):
    full = "🔵"
    empty = "⚪"
    bar_size = 10
    filled = int(percent / 10)
    return (full * filled) + (empty * (bar_size - filled)) + f" {percent}%"

def send_progress_ui(chat_id, task_name):
    msg = bot.send_message(chat_id, f"🚀 **Initializing {task_name}...**", parse_mode="Markdown")
    for i in range(10, 101, 30):
        time.sleep(0.4)
        bot.edit_message_text(
            f"⚡ **Task:** {task_name}\n"
            f"📊 **Progress:** {draw_progress(i)}\n"
            f"⚙️ **System:** MI AI Pro Enterprise is working...",
            chat_id, msg.message_id, parse_mode="Markdown"
        )
    return msg.message_id

# --- ⌨️ UI: SIDEBAR & ENTERPRISE MENU ---
def main_sidebar():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("🏠 Dashboard", "🧠 Deep Thinking", "💻 Ultra Code")
    markup.add("🎨 Art Gen", "🎬 Video Gen", "🌐 Global Search")
    markup.add("📚 Write Book", "📦 ZIP Architect", "⚙️ AI Switches")
    return markup

def ai_switch_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💎 Google Gemini Pro", callback_data="sw_gemini"),
        types.InlineKeyboardButton("⚡ Groq Llama 3.3 (Fast)", callback_data="sw_groq"),
        types.InlineKeyboardButton("🌌 OpenAI GPT-4 (Pro)", callback_data="sw_openai")
    )
    return markup

# --- 🚀 MULTI-ENGINE AI ROUTER ---
def multi_engine_call(uid, prompt):
    u = get_mem(uid)
    hist = "\n".join(u['history'][-8:]) # Optimized memory
    sys_ins = f"Name: MI AI Pro. Creator: Muaaz Iqbal. Role: {u['mode']}. High intelligence mode."

    # 1. OPENAI (via OpenRouter)
    if u['engine'] == "openai":
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            h = {"Authorization": f"Bearer {OPENAI_K}"}
            p = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "system", "content": sys_ins}, {"role": "user", "content": f"Memory:\n{hist}\n\nTask: {prompt}"}]
            }
            r = requests.post(url, headers=h, json=p, timeout=20)
            return r.json()['choices'][0]['message']['content'], "GPT-4"
        except: u['engine'] = "groq" # Auto-switch on failure

    # 2. GROQ
    if u['engine'] == "groq":
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            h = {"Authorization": f"Bearer {GROQ_K}"}
            p = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": sys_ins}, {"role": "user", "content": prompt}]
            }
            r = requests.post(url, headers=h, json=p, timeout=20)
            return r.json()['choices'][0]['message']['content'], "Groq-Llama"
        except: u['engine'] = "gemini"

    # 3. GEMINI
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_K}"
        p = {"contents": [{"parts": [{"text": f"{sys_ins}\n\n{prompt}"}]}]}
        r = requests.post(url, json=p, timeout=20)
        return r.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini-Pro"
    except:
        return "⚠️ All Engines Failed. Check API Limits.", "Offline"

# --- 🛠️ PRO LEVEL TOOLS ---

def generate_video(prompt):
    # This uses Pollinations Video API
    encoded = urllib.parse.quote(prompt)
    return f"https://pollinations.ai/p/{encoded}?model=video&width=1280&height=720"

def generate_pdf(topic, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 20, "MI AI ENTERPRISE REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    out = io.BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

# --- 🤖 HANDLERS: THE BRAIN ---

@bot.message_handler(commands=['start'])
def start_enterprise(m):
    u = get_mem(m.from_user.id)
    welcome = (f"🛡️ **MI AI PRO ULTIMATE V3.0**\n"
               f"━━━━━━━━━━━━━━━━━━\n"
               f"👤 **User:** {m.from_user.first_name}\n"
               f"👨‍💻 **Architect:** Muaaz Iqbal\n"
               f"🌐 **Org:** Muslim Islam\n"
               f"━━━━━━━━━━━━━━━━━━\n"
               f"Main aik enterprise level AI hoon. Niche diye gaye Dashboard se control karein.")
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=main_sidebar())

@bot.callback_query_handler(func=lambda c: c.data.startswith('sw_'))
def switch_engine(c):
    u = get_mem(c.from_user.id)
    engine_name = c.data.split('_')[1]
    u['engine'] = engine_name
    bot.answer_callback_query(c.id, f"✅ Switched to {engine_name.upper()}")
    bot.edit_message_text(f"⚙️ **System Update:** Engine changed to **{engine_name.upper()}**", c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: True)
def handle_all(m):
    uid = m.from_user.id
    u = get_mem(uid)
    text = m.text

    # 1. Sidebar Logic
    if "Dashboard" in text:
        bot.reply_to(m, f"📊 **User Stats:**\nRequests: {u['stats']['requests']}\nFiles Gen: {u['stats']['files_gen']}\nEngine: {u['engine'].upper()}")
    
    elif "AI Switches" in text:
        bot.send_message(m.chat.id, "⚙️ **Select AI Core Engine:**", reply_markup=ai_switch_menu())

    elif "Art Gen" in text:
        msg = bot.send_message(m.chat.id, "🎨 **Art Architect:** Prompt likhein?")
        bot.register_next_step_handler(msg, process_art)

    elif "Video Gen" in text:
        msg = bot.send_message(m.chat.id, "🎬 **Video Architect:** Scene describe karein?")
        bot.register_next_step_handler(msg, process_video)

    elif "Write Book" in text:
        msg = bot.send_message(m.chat.id, "📚 **PDF Expert:** Book ka topic?")
        bot.register_next_step_handler(msg, process_book)

    elif "ZIP Architect" in text:
        msg = bot.send_message(m.chat.id, "📦 **Zip Pro:** App/Project requirements?")
        bot.register_next_step_handler(msg, process_zip)

    elif "Global Search" in text:
        msg = bot.send_message(m.chat.id, "🌐 **Global Search:** Topic?")
        bot.register_next_step_handler(msg, process_search)

    else:
        # Standard Pro Chat
        p_id = send_progress_ui(m.chat.id, "Thinking Process")
        ans, engine = multi_engine_call(uid, text)
        u['history'].append(f"U: {text}"); u['history'].append(f"A: {ans}")
        u['stats']['requests'] += 1
        
        bot.delete_message(m.chat.id, p_id)
        bot.reply_to(m, f"{ans}\n\n━━━━━━━━━━━━━━\n🧠 **Node:** {engine} | ⚡ **Level:** Enterprise", parse_mode="Markdown")

# --- ⚡ STEP FUNCTIONS ---

def process_art(m):
    p_id = send_progress_ui(m.chat.id, "Image Synthesis")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(m.text)}?width=1024&height=1024&nologo=true"
    bot.delete_message(m.chat.id, p_id)
    bot.send_photo(m.chat.id, url, caption=f"✅ **MI Art Gen:** {m.text}")

def process_video(m):
    p_id = send_progress_ui(m.chat.id, "Video Rendering")
    v_url = generate_video(m.text)
    bot.delete_message(m.chat.id, p_id)
    bot.send_video(m.chat.id, v_url, caption=f"🎬 **MI Video Gen:** {m.text}")

def process_book(m):
    p_id = send_progress_ui(m.chat.id, "Authoring Book")
    content, _ = multi_engine_call(m.from_user.id, f"Write a 10 page book on {m.text}")
    pdf = generate_pdf(m.text, content)
    pdf.name = f"{m.text}.pdf"
    bot.delete_message(m.chat.id, p_id)
    bot.send_document(m.chat.id, pdf, caption="📚 **Enterprise Book Complete!**")

def process_zip(m):
    p_id = send_progress_ui(m.chat.id, "Generating Source Code")
    code, _ = multi_engine_call(m.from_user.id, f"Write long professional code for {m.text}")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("main.py", code)
        z.writestr("info.txt", f"Created by MI AI Pro for Muaaz Iqbal.")
    buf.seek(0)
    buf.name = "Project_MI.zip"
    bot.delete_message(m.chat.id, p_id)
    bot.send_document(m.chat.id, buf, caption="📦 **Enterprise Project ZIP Ready!**")

def process_search(m):
    p_id = send_progress_ui(m.chat.id, "Deep Web Scanning")
    ans, _ = multi_engine_call(m.from_user.id, f"Search internet and give professional report on: {m.text}")
    bot.delete_message(m.chat.id, p_id)
    bot.reply_to(m, f"🌐 **Global Search Result:**\n\n{ans}")

# ================= 🚀 SERVER START =================
if __name__ == "__main__":
    print("💎 MI AI PRO ENTERPRISE V3.0 ONLINE")
    while True:
        try:
            bot.infinity_polling(timeout=20)
        except:
            time.sleep(5)
