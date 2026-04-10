import telebot
from telebot import types
import requests, os, time, json, base64, threading, urllib.parse, io, zipfile, sqlite3
from fpdf import FPDF
from datetime import datetime

# ==============================================================
# 👑 MI AI - PUBLIC ENTERPRISE EDITION (THE BOMB PROGRAM)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# ==============================================================

# --- 🔐 API KEYS (Environment Variables se lein ya yahan dalein) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ================= 🗄️ REAL DATABASE (USER DATA COLLECTION) =================
# Ab data memory se delete nahi hoga, properly save hoga
conn = sqlite3.connect('mi_ai_public.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, name TEXT, engine TEXT, mode TEXT, queries INTEGER)''')
conn.commit()

class MI_DataMaster:
    def add_user(self, uid, name):
        c.execute("INSERT OR IGNORE INTO users (uid, name, engine, mode, queries) VALUES (?, ?, 'groq', 'Pro Think', 0)", (uid, name))
        conn.commit()
    
    def get_user(self, uid):
        c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        return c.fetchone()
    
    def update_engine(self, uid, engine):
        c.execute("UPDATE users SET engine=? WHERE uid=?", (engine, uid))
        conn.commit()

    def add_query(self, uid):
        c.execute("UPDATE users SET queries = queries + 1 WHERE uid=?", (uid,))
        conn.commit()

db = MI_DataMaster()
user_sessions = {} # For temporary files like cover images

# ================= 🎨 UI: DEEP SIDEBAR & COLORFUL BUTTONS =================
def public_dashboard():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    m.add("📊 My Dashboard", "🧠 Deep AI Chat", "💻 Mega Code Lab")
    m.add("🖼️ Web Art Gen", "🌐 Smart Google Sync", "🎬 Video Engine")
    m.add("📕 Color PDF Book", "📦 ZIP Project Builder", "⚙️ Switch AI Model")
    m.add("📖 Story Teller", "👁️ Vision Analysis", "🗑️ Reset Memory")
    return m

def ai_switch_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("⚡ Groq 70B (Fast Logic/Code)", callback_data="ai_groq"),
        types.InlineKeyboardButton("💎 Gemini 1.5 Pro (Deep Vision)", callback_data="ai_gemini"),
        types.InlineKeyboardButton("🌌 OpenRouter (GPT/Claude)", callback_data="ai_openrouter")
    )
    return m

# ================= 📊 COLORFUL DIGITAL PROGRESS =================
def digital_progress(chat_id, task_name):
    msg = bot.send_message(chat_id, f"🔴 **{task_name} Started...**", parse_mode="Markdown")
    bars = ["🟥⬜⬜⬜⬜ 20%", "🟥🟥⬜⬜⬜ 40%", "🟥🟥🟥⬜⬜ 60%", "🟥🟥🟥🟥⬜ 80%", "🟩🟩🟩🟩🟩 100%"]
    for b in bars:
        try:
            bot.edit_message_text(f"🔥 **MI AI PROCESSING**\n⚙️ `{task_name}`\n📊 {b}\n⚡ *Please Wait...*", chat_id, msg.message_id, parse_mode="Markdown")
            time.sleep(0.5)
        except: pass
    return msg.message_id

# ================= 🚀 THE 3-AI ENGINE CORE =================
def mega_ai_brain(uid, prompt, sys_role="Super AI Assistant"):
    db.add_query(uid)
    user_data = db.get_user(uid)
    engine = user_data[2] # groq, gemini, openrouter

    sys_prompt = f"Your name is MI AI. Creator: Muaaz Iqbal. Role: {sys_role}. Be professional, beautiful, and highly accurate. Use emojis."

    try:
        if engine == "groq":
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {GROQ_KEY}"}, 
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}
            ).json()
            return res['choices'][0]['message']['content'], "Groq 70B ⚡"
            
        elif engine == "openrouter":
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"}, 
                json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]}
            ).json()
            return res['choices'][0]['message']['content'], "OpenRouter 🌌"
            
        else: # Gemini Fallback & Default
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}", 
                json={"contents": [{"parts": [{"text": f"{sys_prompt}\nUser: {prompt}"}]}]}
            ).json()
            return res['candidates'][0]['content']['parts'][0]['text'], "Gemini Pro 💎"
    except Exception as e:
        return "⚠️ All AI nodes overloaded. Please try again.", "Error"

# ================= 🌐 SMART GOOGLE SYNC (AI + Search) =================
def ai_google_search(uid, query):
    # AI analyzes query, fetches real-time lookalike data, and mixes with image
    img_url = f"https://pollinations.ai/p/{urllib.parse.quote(query)}?width=800&height=400"
    ai_report, node = mega_ai_brain(uid, f"Search Google for latest info, top articles, and deep details about: {query}. Give a colorful, highly detailed report with bullet points.", "Global Web Researcher")
    return ai_report, img_url, node

# ================= 📕 LUXURY PDF & TEMPLATES =================
def build_color_pdf(uid, topic, cover_img_path=None):
    content, _ = mega_ai_brain(uid, f"Write a 50+ page style comprehensive book on '{topic}'. Include Index, Chapters, and conclusion.", "Master Author")
    
    pdf = FPDF()
    # COVER PAGE
    pdf.add_page()
    pdf.set_fill_color(30, 30, 30) # Dark Beautiful Background
    pdf.rect(0, 0, 210, 297, 'F')
    
    if cover_img_path and os.path.exists(cover_img_path):
        pdf.image(cover_img_path, x=20, y=50, w=170)
    else: # AI Auto Cover
        pdf.set_text_color(255, 100, 100)
        pdf.set_font("Arial", 'B', 40)
        pdf.text(30, 100, "MI AI EXCLUSIVE")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 30)
    pdf.text(20, 180, topic[:30].upper())
    pdf.set_font("Arial", size=15)
    pdf.text(20, 200, "Authored by MI AI | Muaaz Iqbal")

    # CONTENT PAGE (Light Theme)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# ================= 📦 MEGA ZIP CODER (Long Project Architect) =================
def zip_project_builder(uid, req):
    sys_req = "Generate a full Python/Web project. Return data strictly as: FILE: filename.ext\nCODE:\ncode_here\n"
    raw_code, _ = mega_ai_brain(uid, req, sys_req)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        try:
            files = raw_code.split("FILE:")[1:]
            for f in files:
                name = f.split("CODE:")[0].strip()
                code = f.split("CODE:")[1].strip()
                z.writestr(name, code)
            z.writestr("MI_AI_README.md", f"# Auto-Generated by MI AI\nCreator: Muaaz Iqbal\nTopic: {req}")
        except:
            z.writestr("logic.txt", raw_code) # Fallback if AI formatting fails
    buf.seek(0)
    return buf

# ================= 🤖 BOT HANDLERS & ROUTING =================

@bot.message_handler(commands=['start'])
def start_public(m):
    db.add_user(m.from_user.id, m.from_user.first_name)
    user_sessions[m.from_user.id] = {"cover_img": None}
    welcome = (f"🌟 **Welcome to MI AI PUBLIC EDITION** 🌟\n\n"
               f"Hello **{m.from_user.first_name}**! I am **MI AI**, a Supreme System created by **Muaaz Iqbal**.\n\n"
               f"🔹 I can write Long Codes & build ZIP files.\n"
               f"🔹 I can create Colorful PDF Books.\n"
               f"🔹 I can do Smart Google Searches with Images.\n"
               f"🔹 I am powered by Groq, Gemini & OpenRouter.\n\n"
               f"👇 *Use the powerful Dashboard below to start!*")
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=public_dashboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith('ai_'))
def switch_ai_model(c):
    engine = c.data.split('_')[1]
    db.update_engine(c.from_user.id, engine)
    bot.answer_callback_query(c.id, f"✅ AI Switched to {engine.upper()}")
    bot.edit_message_text(f"⚙️ **System Updated:** You are now using **{engine.upper()}** Engine.", c.message.chat.id, c.message.message_id)

@bot.message_handler(content_types=['photo'])
def handle_photos(m):
    # Save photo for potential PDF cover or Vision analysis
    f_info = bot.get_file(m.photo[-1].file_id)
    img_data = bot.download_file(f_info.file_path)
    path = f"cover_{m.from_user.id}.jpg"
    with open(path, "wb") as f: f.write(img_data)
    
    if m.from_user.id not in user_sessions: user_sessions[m.from_user.id] = {}
    user_sessions[m.from_user.id]["cover_img"] = path
    
    bot.reply_to(m, "📸 **Image Saved!**\nI can use this as a Cover Image for your next **Color PDF Book**, or click '👁️ Vision Analysis' to analyze it.")

@bot.message_handler(func=lambda m: True)
def public_router(m):
    uid = m.from_user.id
    txt = m.text

    if "⚙️ Switch AI Model" in txt:
        bot.send_message(m.chat.id, "🎛️ **Select AI Core Engine:**", reply_markup=ai_switch_menu())

    elif "📊 My Dashboard" in txt:
        u_data = db.get_user(uid)
        bot.reply_to(m, f"📊 **Your Stats:**\nName: {u_data[1]}\nActive AI: {u_data[2].upper()}\nTotal Queries: {u_data[4]}\nStatus: PRO User 💎")

    elif "💻 Mega Code Lab" in txt:
        msg = bot.send_message(m.chat.id, "💻 **Enter Full Project Details (Code will be deep and long):**")
        bot.register_next_step_handler(msg, step_code)

    elif "📦 ZIP Project Builder" in txt:
        msg = bot.send_message(m.chat.id, "📦 **Enter App Requirements to build a ZIP architecture:**")
        bot.register_next_step_handler(msg, step_zip)

    elif "📕 Color PDF Book" in txt:
        msg = bot.send_message(m.chat.id, "📕 **Enter Book Topic:**\n*(Note: Agar aapne pehle photo bheji hai, wo cover ban jayegi!)*")
        bot.register_next_step_handler(msg, step_pdf)

    elif "🌐 Smart Google Sync" in txt:
        msg = bot.send_message(m.chat.id, "🌐 **What do you want to deep search?**")
        bot.register_next_step_handler(msg, step_search)

    elif "🖼️ Web Art Gen" in txt or "🎬 Video Engine" in txt:
        msg = bot.send_message(m.chat.id, "🎨/🎬 **Enter Prompt for Image/Video:**")
        bot.register_next_step_handler(msg, step_media)

    elif "📖 Story Teller" in txt:
        msg = bot.send_message(m.chat.id, "📖 **Enter Story Topic:**")
        bot.register_next_step_handler(msg, step_story)

    else:
        # Normal Deep Thinking Chat
        mid = digital_progress(m.chat.id, "Deep AI Reasoning")
        ans, node = mega_ai_brain(uid, txt)
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, f"🔥 **MI AI**\n━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Engine:* `{node}`", parse_mode="Markdown")

# --- ⚡ STEP FUNCTIONS (The Heavy Lifters) ---

def step_code(m):
    mid = digital_progress(m.chat.id, "Generating Deep Code")
    ans, node = mega_ai_brain(m.from_user.id, f"Write a very long, highly structured, error-free code for: {m.text}. Add comments.", "Senior Programmer")
    bot.delete_message(m.chat.id, mid)
    bot.reply_to(m, f"💻 **Code Lab Result:**\n\n{ans[:3900]}\n\n🤖 *Powered by {node}*")

def step_zip(m):
    mid = digital_progress(m.chat.id, "Architecting ZIP Folder")
    zip_buf = zip_project_builder(m.from_user.id, m.text)
    zip_buf.name = "MI_Project.zip"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, zip_buf, caption=f"📦 **Complete Project Built!**\nTask: {m.text}")

def step_pdf(m):
    mid = digital_progress(m.chat.id, "Designing Color PDF")
    cover_img = user_sessions.get(m.from_user.id, {}).get("cover_img")
    pdf_buf = build_color_pdf(m.from_user.id, m.text, cover_img)
    pdf_buf.name = f"{m.text[:15]}.pdf"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, pdf_buf, caption=f"📕 **Beautiful Book Created!**\nTopic: {m.text}")

def step_search(m):
    mid = digital_progress(m.chat.id, "Google AI Sync")
    report, img_url, node = ai_google_search(m.from_user.id, m.text)
    bot.delete_message(m.chat.id, mid)
    bot.send_photo(m.chat.id, img_url, caption=f"🌐 **Smart Search Report ({node}):**\n\n{report[:900]}...\n\n🔗 [View Full Google Results](https://www.google.com/search?q={urllib.parse.quote(m.text)})")

def step_media(m):
    p = urllib.parse.quote(m.text)
    bot.send_photo(m.chat.id, f"https://image.pollinations.ai/prompt/{p}?nologo=true", caption=f"🎨 AI Generated: {m.text}")

def step_story(m):
    mid = digital_progress(m.chat.id, "Writing Story")
    ans, _ = mega_ai_brain(m.from_user.id, f"Write a long, beautiful, engaging story about: {m.text}", "Expert Storyteller")
    bot.delete_message(m.chat.id, mid)
    bot.reply_to(m, f"📖 **MI AI Story:**\n\n{ans}")

# ================= 🚀 SERVER BOOT =================
if __name__ == "__main__":
    print("========================================")
    print("🔥 MI AI PUBLIC EDITION IS ONLINE 🔥")
    print("👨‍💻 Architect: Muaaz Iqbal | Muslim Islam")
    print("========================================")
    bot.infinity_polling(timeout=20)
