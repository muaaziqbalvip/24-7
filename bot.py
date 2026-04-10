import telebot
from telebot import types
import requests, os, time, json, base64, threading, urllib.parse, io, zipfile, random
from fpdf import FPDF
from datetime import datetime
from PIL import Image

# ==============================================================
# 👑 MI AI PRO SUPREME - THE ARCHITECT (MUAAZ IQBAL EDITION)
# 🏢 ORGANIZATION: MUSLIM ISLAM | PROJECT: MiTV Network
# ==============================================================

# --- 🔐 Security & Core Config ---
TOKEN = os.getenv("BOT_TOKEN")
GE_K = os.getenv("GEMINI_API_KEY")
GR_K = os.getenv("GROQ_API_KEY")
OR_K = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TOKEN)

# --- 🧠 SUPREME DATABASE & MEMORY SYSTEM ---
class MI_Database:
    def __init__(self):
        self.users = {}

    def get_u(self, uid, name="User"):
        if uid not in self.users:
            self.users[uid] = {
                "name": name,
                "engine": "groq",
                "repo": {},        # Persistent file storage
                "history": [],     # Context memory
                "mode": "Standard",
                "theme": "Red_Dark",
                "stats": {"books": 0, "codes": 0, "searches": 0}
            }
        return self.users[uid]

db = MI_Database()

# --- 📊 PROFESSIONAL PROGRESS & STATUS ---
def update_progress(chat_id, mid, task, percent):
    bars = "🔴" * (percent // 10) + "⚪" * (10 - (percent // 10))
    status_text = (
        f"🚀 **MI AI SUPREME CORE**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚙️ **Task:** `{task}`\n"
        f"📊 **Progress:** [{bars}] {percent}%\n"
        f"👤 **Master:** Muaaz Iqbal"
    )
    try:
        bot.edit_message_text(status_text, chat_id, mid, parse_mode="Markdown")
    except: pass

# --- ⌨️ SUPREME UI & TOOLBARS ---
def get_main_keyboard():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    m.add("📂 Repo Manager", "🧠 Deep Logic", "💻 Full-Stack Arch")
    m.add("🖼️ Art Engine", "🌐 Web Research", "🎬 Video Creator")
    m.add("📕 Luxury Book", "📦 ZIP Factory", "⚙️ AI Control")
    return m

def get_repo_inline(uid):
    u = db.get_u(uid)
    m = types.InlineKeyboardMarkup(row_width=1)
    for filename in list(u['repo'].keys())[:5]: # Show last 5 files
        m.add(types.InlineKeyboardButton(f"📄 {filename}", callback_data=f"view_{filename}"))
    m.add(types.InlineKeyboardButton("🗑️ Clear Repo", callback_data="clear_repo"))
    return m

# --- 🚀 ENGINE: DEEP CODE & LOGIC ---
def call_mi_ai(uid, prompt, system_instruction):
    u = db.get_u(uid)
    memory = "\n".join(u['history'][-10:]) # Long memory recall
    
    # Selecting the beast engine
    if u['engine'] == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GR_K}"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": f"Name: MI AI. Creator: Muaaz Iqbal. {system_instruction}"},
                {"role": "user", "content": f"Previous Data: {memory}\n\nTask: {prompt}"}
            ]
        }
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GE_K}"
        payload = {"contents": [{"parts": [{"text": f"{system_instruction}\n{prompt}"}]}]}

    try:
        res = requests.post(url, json=payload, headers=headers if u['engine']=="groq" else {}, timeout=30).json()
        ans = res['choices'][0]['message']['content'] if u['engine']=="groq" else res['candidates'][0]['content']['parts'][0]['text']
        u['history'].append(f"User: {prompt[:50]}..."); u['history'].append(f"AI: {ans[:50]}...")
        return ans
    except: return "⚠️ Critical Core Error. Switch Engine."

# --- 📂 ZIP & FULL-STACK SYSTEM ---
def build_complex_project(uid, requirements):
    u = db.get_u(uid)
    # AI generates structure
    prompt = f"Write full professional code for: {requirements}. Provide multiple files (e.g. main.py, utils.py, config.json, README.md). Separate files with 'FILE:filename' marker."
    raw_code = call_mi_ai(uid, prompt, "Senior Software Architect")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        files = raw_code.split("FILE:")
        for f in files[1:]:
            lines = f.split("\n")
            fname = lines[0].strip()
            fcontent = "\n".join(lines[1:])
            z.writestr(fname, fcontent)
            u['repo'][fname] = fcontent # Save in repo
        z.writestr("MI_AI_CREDITS.txt", "Project Built by MI AI Pro Supreme.\nMaster: Muaaz Iqbal.")
    
    buf.seek(0)
    return buf

# --- 📕 LUXURY PDF BOOK SYSTEM (WITH IMAGES) ---
def build_luxury_pdf(uid, topic, cover_img_msg=None):
    u = db.get_u(uid)
    content = call_mi_ai(uid, f"Write a 100-page level deep research book content on {topic} with titles, index, and 10 chapters.", "Professional Author")
    
    pdf = FPDF()
    # Cover Page
    pdf.add_page()
    pdf.set_fill_color(180, 0, 0) # Red Luxury Theme
    pdf.rect(0, 0, 210, 297, 'F')
    
    if cover_img_msg: # If user sent a photo
        f_info = bot.get_file(cover_img_msg.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        with open("cover.jpg", "wb") as f: f.write(img_data)
        pdf.image("cover.jpg", x=10, y=50, w=190)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 35)
    pdf.text(30, 40, topic.upper())
    pdf.set_font("Arial", size=15)
    pdf.text(30, 280, f"Published by MI AI Pro | Master: {u['name']}")

    # Content
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, content.encode('latin-1', 'replace').decode('latin-1'))
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# --- 🤖 MAIN MESSAGE HANDLER ---
@bot.message_handler(commands=['start'])
def supreme_start(m):
    u = db.get_u(m.from_user.id, m.from_user.first_name)
    bot.send_message(m.chat.id, f"🔴 **MI AI PRO SUPREME V4.0**\n━━━━━━━━━━━━━━━\nWelcome Master **{u['name']}**.\nSystem is initialized with Deep Research & Coding capabilities.", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def supreme_router(m):
    uid = m.from_user.id
    u = db.get_u(uid)
    text = m.text

    if "Full-Stack Arch" in text:
        msg = bot.send_message(m.chat.id, "💻 **Describe the Full Project Architecture:**")
        bot.register_next_step_handler(msg, step_zip)

    elif "Luxury Book" in text:
        msg = bot.send_message(m.chat.id, "📕 **Enter Book Topic:** (Send a photo after this for the cover!)")
        bot.register_next_step_handler(msg, step_book)

    elif "Web Research" in text:
        msg = bot.send_message(m.chat.id, "🌐 **What do you want to research globally?**")
        bot.register_next_step_handler(msg, step_research)

    elif "📂 Repo Manager" in text:
        bot.send_message(m.chat.id, "📁 **MI AI Repository Console**", reply_markup=get_repo_inline(uid))

    else:
        # Deep Brain Chat
        status = bot.send_message(m.chat.id, "🧠 Analyzing...")
        ans = call_mi_ai(uid, text, "Full Knowledge Expert")
        bot.delete_message(m.chat.id, status.message_id)
        bot.reply_to(m, f"🔴 **MI AI:**\n\n{ans}", parse_mode="Markdown")

# --- ⚡ STEP-BY-STEP FUNCTIONS ---
def step_zip(m):
    mid = bot.send_message(m.chat.id, "🚀 Initializing...").message_id
    update_progress(m.chat.id, mid, "Architecting Files", 30)
    zip_buf = build_complex_project(m.from_user.id, m.text)
    update_progress(m.chat.id, mid, "Compressing Project", 80)
    zip_buf.name = f"{m.text[:10]}.zip"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, zip_buf, caption="📦 **Full-Stack Project Completed.**\nCheck MI Repo for source.")

def step_book(m):
    topic = m.text
    mid = bot.send_message(m.chat.id, "📚 Writing Content...").message_id
    update_progress(m.chat.id, mid, "Generating Research", 40)
    pdf_buf = build_luxury_pdf(m.from_user.id, topic)
    update_progress(m.chat.id, mid, "Styling Layout", 90)
    pdf_buf.name = f"{topic}.pdf"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, pdf_buf, caption=f"📕 **Luxury Edition:** {topic}")

def step_research(m):
    mid = bot.send_message(m.chat.id, "🌐 Scanning Web...").message_id
    update_progress(m.chat.id, mid, "Fetching Articles", 50)
    img_url = f"https://pollinations.ai/p/{urllib.parse.quote(m.text)}?width=800&height=400"
    report = call_mi_ai(m.from_user.id, f"Give detailed report with links and top articles for: {m.text}", "Global Researcher")
    bot.delete_message(m.chat.id, mid)
    bot.send_photo(m.chat.id, img_url, caption=f"🌐 **Research Report:**\n\n{report}\n\n[Google Search Link](https://www.google.com/search?q={urllib.parse.quote(m.text)})")

# ================= 🚀 SERVER EXECUTION =================
if __name__ == "__main__":
    print("💎 MI AI PRO SUPREME IS ONLINE")
    bot.infinity_polling()
