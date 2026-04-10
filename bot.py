import telebot
import requests, os, time, json, base64, threading, urllib.parse, io, zipfile, random
from telebot import types
from fpdf import FPDF
from datetime import datetime
from PIL import Image

# ==============================================================
# 👑 MI AI PRO SUPREME - MASTER VERSION
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | MiTV Network
# 🏢 ORGANIZATION: MUSLIM ISLAM
# ==============================================================

# --- 🔐 Security: GitHub Secret Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# --- 🧠 SUPREME DATABASE & MEMORY REPOSITORY ---
class MI_OS:
    def __init__(self):
        self.users = {}

    def get_u(self, uid, name="User"):
        if uid not in self.users:
            self.users[uid] = {
                "name": name,
                "engine": "groq",
                "repo": {},        # Persistent file storage for ZIPs
                "history": [],     # Global memory context
                "mode": "Standard",
                "current_project": None,
                "stats": {"books": 0, "codes": 0, "searches": 0}
            }
        return self.users[uid]

MI_CORE = MI_OS()

# --- 📊 DIGITAL PROGRESS UI (RED & WHITE THEME) ---
def update_mi_progress(chat_id, mid, task, percent):
    # Professional Progress Bar Design
    bars = "🔴" * (percent // 10) + "⚪" * (10 - (percent // 10))
    status_text = (
        f"🚀 **MI AI SUPREME CORE ENGINE**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **System Task:** `{task}`\n"
        f"📊 **Processing:** [{bars}] {percent}%\n"
        f"👨‍💻 **Architect:** Muaaz Iqbal\n"
        f"📅 **Status:** {datetime.now().strftime('%H:%M:%S')}"
    )
    try:
        bot.edit_message_text(status_text, chat_id, mid, parse_mode="Markdown")
    except: pass

# --- ⌨️ SUPREME UI: SIDEBAR & TOOLBARS ---
def get_supreme_sidebar():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("🏠 Dashboard", "🧠 Deep Think", "💻 Ultra Code Lab")
    markup.add("🖼️ Art Vision", "🌐 Global Research", "🎬 Video Gen")
    markup.add("📕 Luxury PDF Book", "📦 ZIP Factory", "⚙️ AI Control")
    return markup

def ai_control_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚡ Llama 3.3 70B (Fast Coding)", callback_data="set_groq"),
        types.InlineKeyboardButton("💎 Gemini Pro (Deep Logic)", callback_data="set_gemini"),
        types.InlineKeyboardButton("🗑️ Wipe Repository", callback_data="clear_repo")
    )
    return markup

# --- 🚀 CORE ENGINES: LONG CODE & RESEARCH ---
def call_supreme_ai(uid, prompt, system_instruction):
    u = MI_CORE.get_u(uid)
    memory = "\n".join(u['history'][-15:]) # Enhanced memory recall
    
    if u['engine'] == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": f"Name: MI AI. Creator: Muaaz Iqbal. Role: {system_instruction}"},
                {"role": "user", "content": f"Context Memory:\n{memory}\n\nTask: {prompt}"}
            ]
        }
        res = requests.post(url, json=payload, headers=headers).json()
        ans = res['choices'][0]['message']['content']
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": f"{system_instruction}\n{prompt}"}]}]}
        res = requests.post(url, json=payload).json()
        ans = res['candidates'][0]['content']['parts'][0]['text']

    u['history'].append(f"U: {prompt[:100]}"); u['history'].append(f"AI: {ans[:100]}")
    return ans

# --- 📂 ZIP FACTORY: FULL FOLDER STRUCTURE ---
def build_zip_repository(uid, requirements):
    u = MI_CORE.get_u(uid)
    # This prompt forces AI to act as a File System
    prompt = f"""
    Create a complete professional file structure for: {requirements}. 
    You must provide multiple files. Format your response exactly as:
    FILE: folder/filename.ext
    CODE: (the content of the file)
    Repeat this for every file in the project including README.md and index files.
    """
    raw_data = call_supreme_ai(uid, prompt, "Senior Software Architect & Full-Stack Developer")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        chunks = raw_data.split("FILE:")[1:]
        for chunk in chunks:
            try:
                parts = chunk.split("CODE:")
                fname = parts[0].strip()
                fcontent = parts[1].strip()
                z.writestr(fname, fcontent)
                u['repo'][fname] = fcontent # Saving in user's virtual repo
            except: continue
        z.writestr("MI_AI_INFO.txt", f"Architected by MI AI Pro for Muaaz Iqbal.\nTime: {datetime.now()}")
    
    buf.seek(0)
    return buf

# --- 📕 LUXURY PDF BOOK: COLORFUL & IMAGE INTEGRATED ---
def build_luxury_book(uid, topic, cover_img_id=None):
    u = MI_CORE.get_u(uid)
    # Step 1: Deep Research
    research_content = call_supreme_ai(uid, f"Write a 100-page style deep research book on {topic} with Chapters, Index, and Scientific detail.", "Professional Researcher")
    
    pdf = FPDF()
    pdf.add_page()
    
    # LUXURY COVER PAGE
    pdf.set_fill_color(220, 20, 60) # Crimson Red Theme
    pdf.rect(0, 0, 210, 297, 'F')
    
    if cover_img_id:
        f_info = bot.get_file(cover_img_id)
        img_data = bot.download_file(f_info.file_path)
        with open("temp_cover.jpg", "wb") as f: f.write(img_data)
        pdf.image("temp_cover.jpg", x=10, y=60, w=190)
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 35)
    pdf.text(30, 40, topic.upper())
    pdf.set_font("Arial", 'I', 15)
    pdf.text(30, 280, f"Published by MI AI Pro | Master: Muaaz Iqbal")

    # CONTENT PAGES
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, research_content.encode('latin-1', 'replace').decode('latin-1'))
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# --- 🤖 SUPREME HANDLERS ---

@bot.message_handler(commands=['start'])
def supreme_start(m):
    u = MI_CORE.get_u(m.from_user.id, m.from_user.first_name)
    welcome = (f"🔴 **MI AI PRO SUPREME V5.0**\n"
               f"━━━━━━━━━━━━━━━━━━━━\n"
               f"Assalam-o-Alaikum, **Master {u['name']}**.\n\n"
               f"Main aik Ultra-Deep AI hoon jise **Muaaz Iqbal** ne architect kiya hai.\n"
               f"Main Full-Stack Coding, Deep Research, اور Luxury Books بنانے میں مہارت رکھتا ہوں۔")
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=get_supreme_sidebar())

@bot.message_handler(func=lambda m: True)
def supreme_router(m):
    uid = m.from_user.id
    u = MI_CORE.get_u(uid)
    text = m.text

    if "Ultra Code Lab" in text:
        msg = bot.send_message(m.chat.id, "💻 **Enter System Requirements for Full Project Structure:**")
        bot.register_next_step_handler(msg, process_zip_factory)

    elif "Luxury PDF Book" in text:
        msg = bot.send_message(m.chat.id, "📕 **Enter Book Topic:** (Aap cover ke liye picture bhi bhej sakte hain!)")
        bot.register_next_step_handler(msg, process_book_factory)

    elif "Global Research" in text:
        msg = bot.send_message(m.chat.id, "🌐 **What topic should I scan globally?**")
        bot.register_next_step_handler(msg, process_global_research)

    elif "AI Control" in text:
        bot.send_message(m.chat.id, "⚙️ **System Control Panel:**", reply_markup=ai_control_menu())

    elif "Dashboard" in text:
        stats = f"📊 **Muaaz Iqbal's AI Stats:**\nFiles in Repo: {len(u['repo'])}\nRequests: {u['stats']['books'] + u['stats']['codes']}\nEngine: {u['engine'].upper()}"
        bot.reply_to(m, stats)

    else:
        # Standard Pro Chat
        status_mid = bot.send_message(m.chat.id, "🧠 Analyzing Logic...").message_id
        ans = call_supreme_ai(uid, text, "Full Knowledge Expert & Scientific Assistant")
        bot.delete_message(m.chat.id, status_mid)
        bot.reply_to(m, f"🔴 **MI AI:**\n\n{ans}", parse_mode="Markdown")

# --- ⚡ STEP-ACTION LOGICS ---

def process_zip_factory(m):
    mid = bot.send_message(m.chat.id, "🚀 Initializing Core...").message_id
    update_mi_progress(m.chat.id, mid, "Architecting File System", 30)
    zip_buf = build_zip_repository(m.from_user.id, m.text)
    update_mi_progress(m.chat.id, mid, "Compiling Code Structures", 70)
    update_mi_progress(m.chat.id, mid, "Finalizing ZIP Repository", 95)
    
    zip_buf.name = f"{m.text[:15].replace(' ', '_')}_Project.zip"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, zip_buf, caption=f"📦 **Project ZIP Complete!**\nRequirements: {m.text}")

def process_book_factory(m):
    topic = m.text
    mid = bot.send_message(m.chat.id, "📚 Researching Content...").message_id
    update_mi_progress(m.chat.id, mid, "Deep Scanning Topics", 40)
    
    # This checks if the user wants to send a cover image or just text
    pdf_buf = build_luxury_book(m.from_user.id, topic)
    update_mi_progress(m.chat.id, mid, "Styling Luxury Layout", 90)
    
    pdf_buf.name = f"{topic}.pdf"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, pdf_buf, caption=f"📕 **Luxury Edition Book Ready!**\nTopic: {topic}")

def process_global_research(m):
    mid = bot.send_message(m.chat.id, "🌐 Global Scanning...").message_id
    img_url = f"https://pollinations.ai/p/{urllib.parse.quote(m.text)}?width=800&height=400&nologo=true"
    report = call_supreme_ai(m.from_user.id, f"Give deep research report on {m.text} with latest links and top articles.", "Global Researcher")
    bot.delete_message(m.chat.id, mid)
    bot.send_photo(m.chat.id, img_url, caption=f"🌐 **Global Report:**\n\n{report}\n\n🔗 [Deep Scan Link](https://www.google.com/search?q={urllib.parse.quote(m.text)})")

# ================= 🚀 SUPREME BOOT =================
if __name__ == "__main__":
    print("💎 MI AI PRO SUPREME IS ONLINE")
    bot.infinity_polling(timeout=20)
