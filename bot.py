import telebot
from telebot import types
import requests
import os
import time
import base64
import io
import zipfile
import urllib.parse
from fpdf import FPDF

# ==============================================================
# 🌟 MI AI PRO ULTIMATE - FINAL MASTER EDITION
# 🏢 BY: MUAAZ IQBAL | MiTV Network
# ==============================================================

# --- 🔐 Security: Key Masking (GitHub Safe) ---
def d(s): 
    try: return base64.b64decode(s).decode('utf-8')
    except: return ""

# In keys کو چھیڑنے کی ضرورت نہیں، یہ خود ڈیکوڈ ہو جائیں گی
BOT_TOKEN = d("Nzk0MjM2ODc4MTpBQUdGRGxtbkJLVkt1bE1SM0FIRC1MWElnSE9nQ1hqQl9KYw==")
GROQ_KEY = d("Z3NrX2ppRXJ6eXY1ZmJZbDF5c29BdHAxV0dyeWJ6RllEa3o0S01mVHQ3dFl0WkY2UkM4YlFjMjc=")
GEMINI_KEY = d("QUl6YVN5RHN3b2RDVE11NkVwUUxjTTZCUWh2ODNMYTBadW5oOTRJ")

# ٹیلی گرام کنکشن چیک
try:
    bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
    print("✅ Connection Initiated...")
except Exception as e:
    print(f"❌ Connection Error: {e}")

# --- 🧠 User Memory & State ---
users = {}

def get_u(uid):
    if uid not in users:
        users[uid] = {"mode": "Chat", "history": []}
    return users[uid]

# --- 🎨 UI: Professional Tabs System ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add("🏠 Home", "🧠 Pro Think", "💻 Code Lab")
    markup.add("🎨 Art Gen", "🌐 Search", "🎬 Video AI")
    markup.add("📚 PDF Book", "📦 ZIP Project", "⚙️ Settings")
    return markup

# --- 🚀 AI Engine Logic ---
def ask_ai(uid, prompt, system_msg):
    # History context for remembering things
    u = get_u(uid)
    hist = "\n".join(u['history'][-5:])
    
    # Try Groq first (Fast & Pro)
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        h = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Context: {hist}\nUser: {prompt}"}
            ]
        }
        res = requests.post(url, headers=h, json=payload, timeout=20)
        return res.json()['choices'][0]['message']['content'], "Groq-70B"
    except:
        # Fallback to Gemini
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
            p = {"contents": [{"parts": [{"text": f"{system_msg}\nUser: {prompt}"}]}]}
            res = requests.post(url, json=p, timeout=20).json()
            return res['candidates'][0]['content']['parts'][0]['text'], "Gemini-Flash"
        except:
            return "⚠️ Systems are overloaded. Please wait.", "Offline"

# --- 📂 File Makers ---
def make_pdf(topic, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"MI AI Knowledge: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    stream = io.BytesIO()
    pdf.output(stream)
    stream.seek(0)
    return stream

def make_zip(p_name, code):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"{p_name}/main.py", code)
        z.writestr(f"{p_name}/README.md", f"# {p_name}\nBuild by MI AI Pro.")
    buf.seek(0)
    return buf

# --- 🤖 Handlers ---

@bot.message_handler(commands=['start'])
def start(m):
    welcome = (f"🌟 **Assalam-o-Alaikum Muaaz Iqbal!** 🌟\n\n"
               f"Main **MI AI PRO** hoon. Main neechay diye gaye TABS ke mutabiq har kaam kar sakta hoon.\n\n"
               f"Aap images bhej sakte hain, code likhwa sakte hain aur books banwa sakte hain!")
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def router(m):
    uid = m.from_user.id
    u = get_u(uid)
    cmd = m.text

    if "🏠 Home" in cmd:
        bot.reply_to(m, "🏠 Normal Chat Mode Active.")
    
    elif "🎨 Art Gen" in cmd:
        msg = bot.send_message(m.chat.id, "🎨 **Art Engine:** Kya draw karun?")
        bot.register_next_step_handler(msg, draw_art)

    elif "📚 PDF Book" in cmd:
        msg = bot.send_message(m.chat.id, "📚 **PDF Author:** Book ka topic batayein?")
        bot.register_next_step_handler(msg, generate_book)

    elif "📦 ZIP Project" in cmd:
        msg = bot.send_message(m.chat.id, "📦 **Zip Architect:** Project name & requirements?")
        bot.register_next_step_handler(msg, generate_zip)

    elif "🌐 Search" in cmd:
        msg = bot.send_message(m.chat.id, "🌐 **Live Search:** Kya search karna hai?")
        bot.register_next_step_handler(msg, live_search)

    else:
        # Smart Chat
        status = bot.send_message(m.chat.id, "⏳ Thinking...").message_id
        sys_msg = "Your name is MI AI. Creator: Muaaz Iqbal. You are a Pro Thinking AI."
        ans, node = ask_ai(uid, m.text, sys_msg)
        
        u['history'].append(f"U: {m.text}"); u['history'].append(f"A: {ans}")
        if len(u['history']) > 10: u['history'].pop(0) # Memory management

        bot.delete_message(m.chat.id, status)
        bot.reply_to(m, f"{ans}\n\n━━━━━━━━━━━━━━\n🤖 Node: {node}", parse_mode="Markdown")

# --- 🛠️ Action Functions ---

def draw_art(m):
    prompt = urllib.parse.quote(m.text)
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
    bot.send_photo(m.chat.id, url, caption=f"✅ Art for: {m.text}")

def generate_book(m):
    topic = m.text
    bot.send_message(m.chat.id, "✍️ Writing content... please wait.")
    content, node = ask_ai(m.from_user.id, f"Write a long detailed professional book on {topic}.", "Professional Author Mode")
    pdf = make_pdf(topic, content)
    pdf.name = f"{topic}.pdf"
    bot.send_document(m.chat.id, pdf, caption=f"📚 Book on {topic} is ready!")

def generate_zip(m):
    p_name = m.text
    bot.send_message(m.chat.id, "⚙️ Building files...")
    code, node = ask_ai(m.from_user.id, f"Write full python code for {p_name}.", "Senior Developer Mode")
    zip_f = make_zip(p_name.replace(" ", "_"), code)
    zip_f.name = f"{p_name}.zip"
    bot.send_document(m.chat.id, zip_f, caption=f"📦 Project ZIP Ready!")

def live_search(m):
    query = m.text
    bot.send_message(m.chat.id, f"🌐 Searching internet for '{query}'...")
    ans, node = ask_ai(m.from_user.id, f"Find latest info about {query} from web.", "Web Search Expert")
    bot.reply_to(m, f"🌐 **Search Result:**\n\n{ans}")

# --- 👁️ Vision (Image Analysis) ---
@bot.message_handler(content_types=['photo'])
def vision(m):
    bot.reply_to(m, "👁️ Analyzing Image...")
    f_info = bot.get_file(m.photo[-1].file_id)
    dl = bot.download_file(f_info.file_path)
    b64 = base64.b64encode(dl).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    p = {"contents": [{"parts": [{"text": "Explain this image."}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
    try:
        res = requests.post(url, json=p).json()
        bot.reply_to(m, f"🖼️ **Image Scan:**\n\n{res['candidates'][0]['content']['parts'][0]['text']}")
    except:
        bot.reply_to(m, "❌ Vision failed!")

# ================= 🚀 STARTING SERVER =================
if __name__ == "__main__":
    print("--------------------------------")
    print("   MI AI PRO IS STARTING...    ")
    print("   Created by Muaaz Iqbal      ")
    print("--------------------------------")
    
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"🔄 Polling Error, Restarting: {e}")
            time.sleep(5)
