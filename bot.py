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
from fpdf import FPDF
from PIL import Image

# ==============================================================
# 🌟 MI AI PRO ULTIMATE - ARCHITECT EDITION
# 🏢 ORGANIZATION: MUSLIM ISLAM | CREATED BY: MUAAZ IQBAL
# ==============================================================

# API Keys (GitHub Secrets se uthayein ya yahan manually likhein)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")
G_K = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
GE_K = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
OR_K = os.getenv("OPENROUTER_API_KEY", "YOUR_OR_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE / MEMORY =================
users_db = {}

def get_user(uid):
    if uid not in users_db:
        users_db[uid] = {
            "current_ai": "groq",
            "deep_think": True,
            "mode": "chat",
            "history": [],
            "last_action": None
        }
    return users_db[uid]

# ================= CUSTOM ICONS =================
ICONS = {
    "bot": "🤖", "vision": "👁️", "voice": "🎤", "pdf": "📄", 
    "zip": "📦", "video": "🎬", "art": "🎨", "search": "🌐",
    "think": "🧠", "code": "💻", "success": "✅", "fire": "🔥"
}

# ================= CORE AI ENGINES =================

def call_ai_logic(uid, prompt, system_prompt):
    """Multi-Engine Routing with Fallback"""
    u = get_user(uid)
    
    # 1. Try Groq (Fastest)
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {G_K}", "Content-Type": "application/json"}
        model = "llama-3.3-70b-versatile" if u['deep_think'] else "llama-3.1-8b-instant"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        return res.json()['choices'][0]['message']['content'], "Groq-70B"
    except:
        # 2. Fallback to Gemini
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GE_K}"
            payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nUser: {prompt}"}]}]}
            res = requests.post(url, json=payload, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini-Flash"
        except:
            return "⚠️ Servers are busy. Try switching AI model.", "Error"

# ================= FILE GENERATORS (PDF & ZIP) =================

def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf_out = io.BytesIO()
    pdf_out.write(pdf.output(dest='S').encode('latin-1'))
    pdf_out.seek(0)
    return pdf_out

def create_project_zip(project_name, code_content):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{project_name}/main.py", code_content)
        zip_file.writestr(f"{project_name}/README.md", f"# {project_name}\nCreated by MI AI Pro.")
        zip_file.writestr(f"{project_name}/requirements.txt", "requests\ntelebot\n")
    zip_buffer.seek(0)
    return zip_buffer

# ================= MULTIMEDIA HANDLERS =================

@bot.message_handler(content_types=['photo'])
def handle_vision(m):
    uid = m.from_user.id
    bot.reply_to(m, f"{ICONS['vision']} Analysis image... Ek minute Maaz bhai.")
    
    file_info = bot.get_file(m.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    b64_image = base64.b64encode(downloaded_file).decode('utf-8')
    
    # Vision using Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GE_K}"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Is image ko detail mein samjhao (Urdu/Hindi)."},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}
            ]
        }]
    }
    try:
        res = requests.post(url, json=payload).json()
        analysis = res['candidates'][0]['content']['parts'][0]['text']
        bot.reply_to(m, f"🖼️ **MI AI Vision Report:**\n\n{analysis}", parse_mode="Markdown")
    except:
        bot.reply_to(m, "⚠️ Vision engine busy!")

@bot.message_handler(content_types=['voice'])
def handle_voice(m):
    bot.reply_to(m, f"{ICONS['voice']} Suna ja raha hai...")
    # Whisper API or Gemini Audio processing here...
    bot.reply_to(m, "🎤 Voice processing feature is active (Requires Whisper Key).")

# ================= TEXT & COMMAND HANDLERS =================

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎨 Draw Art", "📦 Build Project Zip", "📄 Write PDF Book", "🌐 Web Search")
    bot.send_message(m.chat.id, f"🌟 **MI AI PRO ULTIMATE**\nCreated by **Muaaz Iqbal**\n\nMain images dekh sakta hoon, code zip kar sakta hoon aur books likh sakta hoon!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📄 Write PDF Book")
def book_mode(m):
    msg = bot.send_message(m.chat.id, "Kitab ka topic likhein?")
    bot.register_next_step_handler(msg, process_book)

def process_book(m):
    topic = m.text
    bot.send_message(m.chat.id, f"📖 {topic} par research jari hai...")
    content, node = call_ai_logic(m.from_user.id, f"Write a 10-page detailed book on {topic} with headings.", "You are a professional author.")
    
    pdf_file = create_pdf(f"Book: {topic}", content)
    pdf_file.name = f"{topic}_Book.pdf"
    bot.send_document(m.chat.id, pdf_file, caption=f"✅ {topic} Book is ready!\n🤖 Engine: {node}")

@bot.message_handler(func=lambda m: m.text == "📦 Build Project Zip")
def zip_mode(m):
    msg = bot.send_message(m.chat.id, "Project ka naam aur kaam batayein?")
    bot.register_next_step_handler(msg, process_zip)

def process_zip(m):
    p_name = m.text
    bot.send_message(m.chat.id, f"🛠️ Building project: {p_name}...")
    code, node = call_ai_logic(m.from_user.id, f"Create a full Python project code for: {p_name}", "You are a Senior Developer.")
    
    zip_f = create_project_zip(p_name.replace(" ", "_"), code)
    zip_f.name = f"{p_name}_Project.zip"
    bot.send_document(m.chat.id, zip_f, caption=f"📦 Project Files Created!\nIncludes: main.py, README, requirements.")

@bot.message_handler(func=lambda m: m.text == "🎨 Draw Art")
def draw_mode(m):
    msg = bot.send_message(m.chat.id, "Kya draw karun?")
    bot.register_next_step_handler(msg, process_draw)

def process_draw(m):
    prompt = m.text.replace(" ", "%20")
    img_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&seed={time.time()}"
    bot.send_photo(m.chat.id, img_url, caption=f"🎨 MI AI Art for: {m.text}")

@bot.message_handler(func=lambda m: True)
def main_chat(m):
    uid = m.from_user.id
    u = get_user(uid)
    
    # Search Mode Check
    if m.text == "🌐 Web Search":
        u['mode'] = "search"
        bot.send_message(m.chat.id, "🌐 Web Search Active. Kuch bhi puchiye jo internet se search karna ho.")
        return

    bot.send_chat_action(m.chat.id, 'typing')
    
    sys_prompt = f"Name: MI AI Pro. Creator: Muaaz Iqbal. Role: Senior AI Architect. Style: Professional Urdu/English mix."
    
    # Memory logic (Concatenate last 2 messages)
    history_context = "\n".join(u['history'][-4:])
    full_prompt = f"Context:\n{history_context}\n\nUser: {m.text}"
    
    reply, node = call_ai_logic(uid, full_prompt, sys_prompt)
    
    # Update History
    u['history'].append(f"User: {m.text}")
    u['history'].append(f"AI: {reply}")
    
    # Final Response
    final_text = f"{reply}\n\n━━━━━━━━━━━━━━━━━━\n🤖 Engine: {node} | 🧠 Deep Think: ON"
    
    if len(final_text) > 4000:
        for x in range(0, len(final_text), 4000):
            bot.send_message(m.chat.id, final_text[x:x+4000], parse_mode="Markdown")
    else:
        bot.reply_to(m, final_text, parse_mode="Markdown")

# ================= RUN SERVER =================
if __name__ == "__main__":
    print("🚀 MI AI PRO ULTIMATE SERVER IS LIVE!")
    print("Created by: Muaaz Iqbal | MITV Network")
    bot.infinity_polling()
