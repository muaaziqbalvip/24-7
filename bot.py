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
# 🌟 MI AI PRO ULTIMATE - ARCHITECT: MUAAZ IQBAL
# 🏢 ORGANIZATION: MUSLIM ISLAM | PROJECT: MiTV Network
# ==============================================================

# --- 🔐 Security: GitHub Secret Variables ---
# In variables ko GitHub Settings > Secrets me add karein
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# --- 🧠 DATABASE & DEEP MEMORY ---
users_db = {}

def get_user(uid, name="User"):
    if uid not in users_db:
        users_db[uid] = {
            "name": name,
            "current_tab": "Home",
            "history": [],
            "ai_engine": "groq", # Default Engine
            "deep_think": True,
        }
    return users_db[uid]

# --- 🎨 UI: PERMANENT SIDEBAR TABS ---
def get_sidebar_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("🏠 Home", "🧠 Pro Mode", "💻 Code Lab")
    markup.add("🎨 Art Gen", "🌐 Web Search", "🎬 Video AI")
    markup.add("📚 PDF Book", "📦 ZIP Project", "⚙️ Settings")
    return markup

# --- 🚀 MASTER AI LOGIC ---
def call_pro_ai(uid, prompt, sys_instruction):
    u = get_user(uid)
    # Memory Context (Last 6 messages recall)
    context = "\n".join(u['history'][-6:])
    
    # 1. Primary Engine: Groq (Llama 3.3 70B - Fastest Reasoning)
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": sys_instruction},
                {"role": "user", "content": f"Context Memory:\n{context}\n\nActual Prompt: {prompt}"}
            ],
            "temperature": 0.5 if u['deep_think'] else 0.8
        }
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        return res.json()['choices'][0]['message']['content'], "Groq-Pro-70B"
    except:
        # 2. Fallback: Gemini (High Intelligence)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            payload = {"contents": [{"parts": [{"text": f"{sys_instruction}\n\nContext:\n{context}\n\nUser: {prompt}"}]}]}
            res = requests.post(url, json=payload, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini-Pro"
        except:
            return "⚠️ Connection Error with AI Cores. Please check API Keys.", "Offline"

# --- 📂 TOOL LOGIC: PDF & ZIP ---
def create_pdf(topic, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"MI AI Knowledge: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def create_zip(p_name, code):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"{p_name}/main.py", code)
        z.writestr(f"{p_name}/README.md", f"# {p_name}\nCreated by MI AI Pro for Muaaz Iqbal.")
    buf.seek(0)
    return buf

# --- 🤖 HANDLERS ---

@bot.message_handler(commands=['start'])
def start_bot(m):
    uid = m.from_user.id
    u = get_user(uid, m.from_user.first_name)
    bot.send_message(m.chat.id, "🚀 **Booting MI AI Pro Ultimate...**", parse_mode="Markdown")
    time.sleep(1)
    
    welcome = (f"🌟 **Assalam-o-Alaikum, {m.from_user.first_name}!**\n\n"
               f"Main MI AI Pro hoon, jise **MUAAZ IQBAL** ne banaya hai.\n"
               f"Main coding, search, art aur file processing me expert hoon.\n\n"
               f"Niche diye gaye **Side-Tabs** se kaam shuru karein 👇")
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=get_sidebar_menu())

@bot.message_handler(func=lambda m: True)
def main_router(m):
    uid = m.from_user.id
    u = get_user(uid)
    text = m.text

    # --- TAB NAVIGATION LOGIC ---
    if "Home" in text:
        bot.reply_to(m, "🏠 **Home Mode:** Mujhse normal chat karein.")
    
    elif "Art Gen" in text:
        msg = bot.send_message(m.chat.id, "🎨 **Art Mode:** Kya draw karun Muaaz bhai?")
        bot.register_next_step_handler(msg, process_art)

    elif "PDF Book" in text:
        msg = bot.send_message(m.chat.id, "📚 **PDF Engine:** Book ka topic batayein?")
        bot.register_next_step_handler(msg, process_pdf)

    elif "ZIP Project" in text:
        msg = bot.send_message(m.chat.id, "📦 **ZIP Architect:** Project ka naam aur detail batayein?")
        bot.register_next_step_handler(msg, process_zip)

    elif "Web Search" in text:
        msg = bot.send_message(m.chat.id, "🌐 **Live Search:** Kya search karna hai?")
        bot.register_next_step_handler(msg, process_search)

    else:
        # Standard Smart Chat with Memory
        s_id = bot.send_message(m.chat.id, "🧠 Thinking...").message_id
        sys_p = f"You are MI AI Pro. Creator: Muaaz Iqbal. Tone: Professional & Scientific."
        ans, node = call_pro_ai(uid, text, sys_p)
        u['history'].append(f"U: {text}"); u['history'].append(f"A: {ans}")
        
        bot.delete_message(m.chat.id, s_id)
        bot.reply_to(m, f"{ans}\n\n━━━━━━━━━━━━━━\n🤖 **Engine:** {node} | 🧠 **Pro Thinking: ON**", parse_mode="Markdown")

# --- ⚙️ PROCESSING FUNCTIONS ---

def process_art(m):
    prompt = urllib.parse.quote(m.text)
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
    bot.send_photo(m.chat.id, url, caption=f"✅ **Art Generated for:** {m.text}")

def process_pdf(m):
    topic = m.text
    bot.send_message(m.chat.id, "✍️ **Writing book content...**")
    content, _ = call_pro_ai(m.from_user.id, f"Write a professional detailed book on {topic} with 5 chapters.", "Senior Author")
    pdf_buf = create_pdf(topic, content)
    pdf_buf.name = f"{topic}.pdf"
    bot.send_document(m.chat.id, pdf_buf, caption=f"📚 **MI AI Book Ready!**")

def process_zip(m):
    p_name = m.text
    bot.send_message(m.chat.id, "🛠️ **Writing Full Code Project...**")
    code, _ = call_pro_ai(m.from_user.id, f"Write full professional python code for {p_name}.", "Software Architect")
    zip_buf = create_zip(p_name.replace(" ", "_"), code)
    zip_buf.name = f"{p_name}.zip"
    bot.send_document(m.chat.id, zip_buf, caption=f"📦 **Project ZIP Complete!**")

def process_search(m):
    query = m.text
    bot.send_message(m.chat.id, f"🌐 **Searching internet for '{query}'...**")
    ans, _ = call_pro_ai(m.from_user.id, f"Perform a Google search and explain: {query}", "Web Researcher")
    bot.reply_to(m, f"🌐 **Search Result:**\n\n{ans}")

# --- 👁️ VISION HANDLING ---
@bot.message_handler(content_types=['photo'])
def handle_vision(m):
    bot.reply_to(m, "👁️ **Scanning Image...**")
    file_info = bot.get_file(m.photo[-1].file_id)
    dl = bot.download_file(file_info.file_path)
    b64 = base64.b64encode(dl).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": "Explain this image for Muaaz Iqbal."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    try:
        res = requests.post(url, json=payload).json()
        bot.reply_to(m, f"🖼️ **Vision Insight:**\n\n{res['candidates'][0]['content']['parts'][0]['text']}")
    except:
        bot.reply_to(m, "❌ Vision Error!")

# ================= 🚀 STARTING SERVER =================
if __name__ == "__main__":
    print("💎 MI AI PRO ULTIMATE IS LIVE!")
    bot.infinity_polling()
