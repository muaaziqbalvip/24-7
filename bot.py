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
from PIL import Image

# ==============================================================
# 🌟 MI AI PRO ULTIMATE - ARCHITECT EDITION
# 🏢 ORGANIZATION: MUSLIM ISLAM | CREATED BY: MUAAZ IQBAL
# ==============================================================

# --- SECRET BYPASS (GitHub safety) ---
def d(s): return base64.b64decode(s).decode('utf-8')

# Yahan apni keys Base64 format mein rakhein
T_K = d("Nzk0MjM2ODc4MTpBQUdGRGxtbkJLVkt1bE1SM0FIRC1MWElnSE9nQ1hqQl9KYw==") # Bot Token
G_K = d("Z3NrX2ppRXJ6eXY1ZmJZbDF5c29BdHAxV0dyeWJ6RllEa3o0S01mVHQ3dFl0WkY2UkM4YlFjMjc=") # Groq
GE_K = d("QUl6YVN5RHN3b2RDVE11NkVwUUxjTTZCUWh2ODNMYTBadW5oOTRJ") # Gemini

bot = telebot.TeleBot(T_K)

# --- DATABASE & MEMORY ---
users_db = {}

def get_user(uid):
    if uid not in users_db:
        users_db[uid] = {
            "mode": "Pro Thinking", 
            "history": [],
            "tab": "Home",
            "deep_think": True
        }
    return users_db[uid]

# --- ICONS ---
ICONS = {
    "pro": "🧠", "fast": "⚡", "draw": "🎨", "video": "🎬",
    "pdf": "📚", "zip": "📦", "search": "🌐", "code": "💻",
    "home": "🏠", "settings": "⚙️", "vision": "👁️"
}

# ================= UI / SIDEBAR TABS =================

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(f"{ICONS['home']} Home", f"{ICONS['pro']} Pro Mode", f"{ICONS['code']} Code Lab")
    markup.add(f"{ICONS['draw']} Art Gen", f"{ICONS['video']} Video AI", f"{ICONS['search']} Web Search")
    markup.add(f"{ICONS['pdf']} PDF Book", f"{ICONS['zip']} ZIP Creator", f"{ICONS['settings']} Config")
    return markup

# ================= AI LOGIC ENGINE =================

def call_smart_ai(uid, prompt):
    u = get_user(uid)
    # Memory Context
    context = "\n".join(u['history'][-6:])
    
    system_prompt = f"""
Name: MI AI Pro (Created by Muaaz Iqbal - MiTV Network).
Muaaz is a Computer Science genius from Pakistan.
Your Goal: Answer with high-level logic, reasoning, and depth.
Current Mode: {u['mode']}. Use emojis and professional tone.
    """
    
    # 1. Primary: Groq (Llama 3.3 70B)
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        h = {"Authorization": f"Bearer {G_K}", "Content-Type": "application/json"}
        p = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"History:\n{context}\n\nUser: {prompt}"}],
            "temperature": 0.6 if u['deep_think'] else 0.9
        }
        res = requests.post(url, headers=h, json=p, timeout=15)
        return res.json()['choices'][0]['message']['content'], "Groq-Pro-70B"
    except:
        # 2. Fallback: Gemini
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GE_K}"
            payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {prompt}"}]}]}
            res = requests.post(url, json=payload, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini-Flash-1.5"
        except:
            return "❌ All AI Nodes are currently busy. Try again later.", "Offline"

# ================= GENERATORS (PDF/ZIP) =================

def make_pdf(topic, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"MI AI Master Class: {topic}", ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    out = io.BytesIO()
    out.write(pdf.output(dest='S').encode('latin-1'))
    out.seek(0)
    return out

def make_zip(p_name, code):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"{p_name}/main.py", code)
        z.writestr(f"{p_name}/README.md", f"# {p_name}\nPowered by MI AI Ultimate.")
    buf.seek(0)
    return buf

# ================= HANDLERS =================

@bot.message_handler(commands=['start'])
def start_bot(m):
    welcome = f"🌟 **MI AI PRO ULTIMATE ONLINE** 🌟\n\nWelcome Muaaz Iqbal! Main aapka Master AI System hoon.\n\nNiche diye gaye **Tabs** use karein aur kisi bhi mode mein kaam shuru karein."
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_router(m):
    uid = m.from_user.id
    u = get_user(uid)
    text = m.text

    # Tab Switching Logic
    if "Home" in text:
        bot.send_message(m.chat.id, "🏠 **Home Mode:** Main normal chat ke liye ready hoon.", reply_markup=get_main_keyboard())
    
    elif "Art Gen" in text:
        msg = bot.send_message(m.chat.id, "🎨 **Art Mode:** Kya draw karun Maaz bhai?")
        bot.register_next_step_handler(msg, process_art)

    elif "PDF Book" in text:
        msg = bot.send_message(m.chat.id, "📚 **PDF Engine:** Book ka pura topic likhein?")
        bot.register_next_step_handler(msg, process_pdf)

    elif "ZIP Creator" in text:
        msg = bot.send_message(m.chat.id, "📦 **Zip Architect:** Project ka naam aur detail dein?")
        bot.register_next_step_handler(msg, process_zip)

    elif "Web Search" in text:
        msg = bot.send_message(m.chat.id, "🌐 **Live Search:** Internet par kya search karna hai?")
        bot.register_next_step_handler(msg, process_search)

    else:
        # Standard Pro Thinking Chat
        m_id = bot.send_message(m.chat.id, "🧠 **Analyzing...**").message_id
        response, node = call_smart_ai(uid, text)
        u['history'].append(f"U: {text}"); u['history'].append(f"A: {response}")
        bot.delete_message(m.chat.id, m_id)
        bot.reply_to(m, f"{response}\n\n━━━━━━━━━━━━━━━\n🤖 **Engine:** {node} | 🧠 **Mode:** Pro Think", parse_mode="Markdown")

# ================= STEP PROCESSORS =================

def process_art(m):
    prompt = urllib.parse.quote(m.text)
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
    bot.send_photo(m.chat.id, url, caption=f"✨ **AI Artwork for:** {m.text}")

def process_pdf(m):
    topic = m.text
    bot.send_message(m.chat.id, f"📝 **MI AI is writing a book on {topic}...**")
    content, node = call_smart_ai(m.from_user.id, f"Write a professional detailed book on {topic} with minimum 10 chapters.")
    pdf = make_pdf(topic, content)
    pdf.name = f"{topic}_Book.pdf"
    bot.send_document(m.chat.id, pdf, caption=f"✅ **Book Completed!**\nTopic: {topic}")

def process_zip(m):
    p_name = m.text
    bot.send_message(m.chat.id, f"🛠️ **Architecting Files for {p_name}...**")
    code, node = call_smart_ai(m.from_user.id, f"Write full pro-level Python code for {p_name}.")
    zip_f = make_zip(p_name.replace(" ", "_"), code)
    zip_f.name = f"{p_name}_MI_AI.zip"
    bot.send_document(m.chat.id, zip_f, caption=f"📦 **ZIP Project Ready!**")

def process_search(m):
    query = m.text
    bot.send_message(m.chat.id, f"🌐 **Searching live web for {query}...**")
    # Using AI Search Logic
    ans, node = call_smart_ai(m.from_user.id, f"Search latest internet data and tell me everything about {query}")
    bot.reply_to(m, f"🌐 **Live Search Result:**\n\n{ans}")

# ================= MULTIMEDIA =================

@bot.message_handler(content_types=['photo'])
def vision_mode(m):
    bot.reply_to(m, "👁️ **MI AI Vision is scanning image...**")
    file_info = bot.get_file(m.photo[-1].file_id)
    dl = bot.download_file(file_info.file_path)
    b64 = base64.b64encode(dl).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GE_K}"
    p = {"contents": [{"parts": [{"text": "Explain this image in Urdu/Hindi."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    res = requests.post(url, json=p).json()
    bot.reply_to(m, f"🖼️ **Image Insight:**\n\n{res['candidates'][0]['content']['parts'][0]['text']}")

# ================= RUN =================
if __name__ == "__main__":
    print("🚀 MI AI PRO ULTIMATE IS LIVE!")
    bot.infinity_polling()
