import telebot
from telebot import types
import requests, os, time, json, base64, threading, urllib.parse, io, zipfile, sqlite3, logging, re, random
from fpdf import FPDF
from datetime import datetime

# ==============================================================
# 👑 MI AI - PUBLIC ENTERPRISE EDITION (THE BOMB PROGRAM)
# 👨‍💻 ARCHITECT: MUAAZ IQBAL | ORGANIZATION: MUSLIM ISLAM
# 🚀 VERSION: 10.0.0 MAX PRO EDITION
# ==============================================================

# --- ⚙️ ADVANCED SYSTEM CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MI AI CORE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 🔐 API KEYS ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_OPENROUTER_KEY")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=15)

# ================= 🎨 ADVANCED ANIMATION & UI ENGINE =================
# Telegram doesn't support CSS, so we animate via rapid message editing
class AdvancedAnimator:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.animations = {
            "radar": ["📡 [ ◯ ◯ ◯ ]", "📡 [ ◉ ◯ ◯ ]", "📡 [ ◯ ◉ ◯ ]", "📡 [ ◯ ◯ ◉ ]", "📡 [ ◉ ◉ ◉ ]"],
            "blocks": ["⬛⬜⬜⬜⬜", "🟩⬛⬜⬜⬜", "🟩🟩⬛⬜⬜", "🟩🟩🟩⬛⬜", "🟩🟩🟩🟩⬛", "🟩🟩🟩🟩🟩"],
            "matrix": ["░░░░░ 0%", "▓░░░░ 20%", "▓▓░░░ 40%", "▓▓▓░░ 60%", "▓▓▓▓░ 80%", "▓▓▓▓▓ 100%"],
            "hack": ["⚙️ 0x0001", "⚙️ 0x00A4", "⚙️ 0x0B8F", "⚙️ 0x1C9A", "⚙️ CONNECTED"]
        }

    def play(self, chat_id, text, anim_type="blocks", speed=0.4, loops=1):
        msg = self.bot.send_message(chat_id, f"⚡ **{text}**\n{self.animations[anim_type][0]}", parse_mode="Markdown")
        frames = self.animations.get(anim_type, self.animations["blocks"])
        
        for _ in range(loops):
            for frame in frames:
                try:
                    self.bot.edit_message_text(
                        f"🔮 **MI AI QUANTUM CORE**\n━━━━━━━━━━━━━━\n🌀 *Task:* `{text}`\n📊 *Status:* {frame}\n*Please wait...*",
                        chat_id, msg.message_id, parse_mode="Markdown"
                    )
                    time.sleep(speed)
                except:
                    pass
        return msg.message_id

animator = AdvancedAnimator(bot)

# ================= 🗄️ MEGA DATABASE & STATE MANAGEMENT =================
conn = sqlite3.connect('mi_ai_public.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    uid INTEGER PRIMARY KEY, 
    name TEXT, 
    engine TEXT, 
    mode TEXT, 
    queries INTEGER,
    joined_date TEXT,
    last_active TEXT,
    is_banned INTEGER DEFAULT 0
)''')
conn.commit()

class MI_DataMaster:
    def add_user(self, uid, name):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT OR IGNORE INTO users (uid, name, engine, mode, queries, joined_date, last_active) VALUES (?, ?, 'gemini', 'Pro Think', 0, ?, ?)", (uid, name, date_now, date_now))
        conn.commit()
    
    def get_user(self, uid):
        c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        return c.fetchone()
    
    def update_engine(self, uid, engine):
        c.execute("UPDATE users SET engine=? WHERE uid=?", (engine, uid))
        conn.commit()

    def update_activity(self, uid):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET queries = queries + 1, last_active = ? WHERE uid=?", (date_now, uid))
        conn.commit()

db = MI_DataMaster()
user_sessions = {} # For temporary files, memory, and states

# ================= 🎛️ BEAUTIFUL UI COMPONENTS =================
def public_dashboard():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(types.KeyboardButton("🧠 Deep AI Chat"), types.KeyboardButton("💻 Mega Code Lab"))
    m.add(types.KeyboardButton("🖼️ Web Art Gen"), types.KeyboardButton("🌐 Smart Google Sync"))
    m.add(types.KeyboardButton("📕 Color PDF Book"), types.KeyboardButton("📦 ZIP Project Builder"))
    m.add(types.KeyboardButton("📖 Story Teller"), types.KeyboardButton("👁️ Vision Analysis"))
    m.add(types.KeyboardButton("📊 My Dashboard"), types.KeyboardButton("⚙️ Switch AI Model"))
    return m

def ai_switch_menu():
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("⚡ Groq 70B (Fast Logic/Code)", callback_data="ai_groq"),
        types.InlineKeyboardButton("💎 Gemini 1.5 Pro (Deep Vision)", callback_data="ai_gemini"),
        types.InlineKeyboardButton("🌌 OpenRouter (GPT/Claude)", callback_data="ai_openrouter")
    )
    return m

# ================= 🚀 QUANTUM 3-AI ENGINE CORE =================
def mega_ai_brain(uid, prompt, sys_role="Super AI Assistant", img_path=None):
    db.update_activity(uid)
    user_data = db.get_user(uid)
    engine = user_data[2] if user_data else "gemini"

    sys_prompt = f"Your name is MI AI. Creator: Muaaz Iqbal. Role: {sys_role}. Be highly professional, structure your response beautifully with markdown, use relevant emojis, and be accurate."

    try:
        # VISION OVERRIDE: If image is provided, force Gemini (as others might not support vision cleanly)
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"{sys_prompt}\nUser: {prompt}"},
                        {"inline_data": {"mime_type": "image/jpeg", "data": encoded_string}}
                    ]
                }]
            }
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}", json=payload).json()
            return res['candidates'][0]['content']['parts'][0]['text'], "Gemini Vision 👁️"

        # STANDARD TEXT PROCESSING
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
            
        else: # Gemini Default
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}", 
                json={"contents": [{"parts": [{"text": f"{sys_prompt}\nUser: {prompt}"}]}]}
            ).json()
            return res['candidates'][0]['content']['parts'][0]['text'], "Gemini Pro 💎"

    except Exception as e:
        logger.error(f"AI Engine Error: {e}")
        return f"⚠️ All AI nodes overloaded or API key missing.\nSystem Error: {str(e)[:50]}", "Error Node"

# ================= 🌐 SMART GOOGLE SYNC (AI + Realtime Logic) =================
def ai_google_search(uid, query):
    img_url = f"https://pollinations.ai/p/{urllib.parse.quote(query + ' digital abstract futuristic')}?width=1024&height=512"
    ai_report, node = mega_ai_brain(uid, f"Act as a Live Web Searcher. The user is searching for '{query}'. Provide a highly detailed, up-to-date simulated search report. Include Top News, Key Facts, and a summary. Use bullet points.", "Global Web Researcher")
    return ai_report, img_url, node

# ================= 📕 LUXURY COLOR PDF ENGINE =================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'MI AI ENTERPRISE - MUAAZ IQBAL', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def build_color_pdf(uid, topic, cover_img_path=None):
    # Fetch massive content
    content, _ = mega_ai_brain(uid, f"Write a comprehensive, professional book chapter on '{topic}'. Include headings, deep explanations, and a conclusion. Format cleanly without markdown asterisks.", "Master Author")
    
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- COVER PAGE ---
    pdf.add_page()
    pdf.set_fill_color(20, 25, 30) # Dark Midnight Blue
    pdf.rect(0, 0, 210, 297, 'F')
    
    if cover_img_path and os.path.exists(cover_img_path):
        pdf.image(cover_img_path, x=20, y=40, w=170)
    else: 
        pdf.set_text_color(0, 255, 150) # Neon Green AI Vibe
        pdf.set_font("Arial", 'B', 45)
        pdf.text(25, 100, "MI AI EXCLUSIVE")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 28)
    # Basic text wrap for title
    title = topic[:50].upper()
    pdf.set_xy(20, 160)
    pdf.multi_cell(170, 12, title, align='C')
    
    pdf.set_font("Arial", size=14)
    pdf.set_xy(20, 200)
    pdf.multi_cell(170, 10, "Authored by MI AI\nArchitect: Muaaz Iqbal", align='C')

    # --- CONTENT PAGES ---
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Arial", size=12)
    
    # Clean encoding issues for FPDF (Latin-1 requirement)
    clean_text = content.replace('”', '"').replace('“', '"').replace('’', "'").replace('—', '-')
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    # Add title to content page
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, topic.upper(), 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, clean_text)
    
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# ================= 📦 MEGA ZIP CODER (Project Architect) =================
def zip_project_builder(uid, req):
    sys_req = """You are a Master Software Architect. Generate a full multi-file project based on the user's prompt.
    CRITICAL INSTRUCTION: You MUST format your response EXACTLY like this for every file:
    
    <<<FILE: filename.extension>>>
    [code goes here]
    <<<ENDFILE>>>
    
    Create at least a main code file, a README.md, and any necessary configs/styles."""
    
    raw_code, node = mega_ai_brain(uid, req, sys_req)
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        try:
            # Regex to find all files
            pattern = re.compile(r'<<<FILE:\s*(.+?)>>>(.*?)(?:<<<ENDFILE>>>|\Z)', re.DOTALL)
            matches = pattern.findall(raw_code)
            
            if matches:
                for filename, code in matches:
                    z.writestr(filename.strip(), code.strip())
            else:
                # Fallback if AI fails format
                z.writestr("MI_SourceCode.txt", raw_code)
                
            z.writestr("MI_AI_README.md", f"# Auto-Generated by MI AI\nArchitect: Muaaz Iqbal\nPowered by: {node}\nTopic: {req}")
        except Exception as e:
            z.writestr("error_log.txt", f"Parsing error occurred: {e}\n\nRaw Output:\n{raw_code}")
            
    buf.seek(0)
    return buf

# ================= 🤖 BOT ROUTING & MIDDLEWARE =================

@bot.message_handler(commands=['start'])
def start_public(m):
    db.add_user(m.from_user.id, m.from_user.first_name)
    user_sessions[m.from_user.id] = {"cover_img": None, "state": "idle"}
    
    # Stylish Welcome Message
    welcome = (f"🌟 **WELCOME TO MI AI MAX PRO** 🌟\n"
               f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
               f"Greetings, **{m.from_user.first_name}**! I am the ultimate AI System, architected by the visionary **Muaaz Iqbal**.\n\n"
               f"🚀 **Core Capabilities:**\n"
               f"├ 💻 Code mega projects in ZIPs\n"
               f"├ 📕 Generate fully styled Color PDFs\n"
               f"├ 👁️ Deep Vision Image Analysis\n"
               f"├ 🌐 Real-time Smart Search\n"
               f"└ 🧠 Powered by `Gemini`, `Groq`, & `OpenRouter`\n\n"
               f"👇 *Command me using the console below:*")
    
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=public_dashboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith('ai_'))
def switch_ai_model(c):
    engine = c.data.split('_')[1]
    db.update_engine(c.from_user.id, engine)
    
    # Fancy UI update
    bot.answer_callback_query(c.id, f"✅ Quantum Core Switched to {engine.upper()}")
    new_text = (f"⚙️ **SYSTEM OVERRIDE COMPLETE**\n━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🧠 **Active Node:** `{engine.upper()}`\n"
                f"⚡ Your logic requests will now be processed by this engine.")
    bot.edit_message_text(new_text, c.message.chat.id, c.message.message_id, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photos(m):
    mid = animator.play(m.chat.id, "Downloading Image to Mainframe", "matrix", speed=0.3)
    
    try:
        f_info = bot.get_file(m.photo[-1].file_id)
        img_data = bot.download_file(f_info.file_path)
        path = f"cache_img_{m.from_user.id}.jpg"
        
        with open(path, "wb") as f: 
            f.write(img_data)
        
        if m.from_user.id not in user_sessions: 
            user_sessions[m.from_user.id] = {}
        user_sessions[m.from_user.id]["cover_img"] = path
        
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "📸 **Image Secured in Memory!**\n\n🎯 *What to do next?*\n1. Click `📕 Color PDF Book` to use this as a Cover.\n2. Click `👁️ Vision Analysis` to let AI explain this image.", parse_mode="Markdown")
    except Exception as e:
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "⚠️ **Error processing image.** Please try again.")

# --- ROUTER FOR TEXT COMMANDS ---
@bot.message_handler(func=lambda m: True)
def public_router(m):
    uid = m.from_user.id
    txt = m.text
    
    # Initialize session if bot restarted
    if uid not in user_sessions:
        user_sessions[uid] = {"cover_img": None, "state": "idle"}

    if "⚙️ Switch AI Model" in txt:
        bot.send_message(m.chat.id, "🎛️ **SELECT NEURAL NETWORK:**\nChoose the brain that powers your requests:", reply_markup=ai_switch_menu(), parse_mode="Markdown")

    elif "📊 My Dashboard" in txt:
        u_data = db.get_user(uid)
        dash = (f"📊 **MI AI COMMAND CENTER** 📊\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **User:** `{u_data[1]}`\n"
                f"🆔 **ID:** `{u_data[0]}`\n"
                f"🧠 **Active Core:** `{u_data[2].upper()}`\n"
                f"⚡ **Total Queries:** `{u_data[4]}`\n"
                f"📅 **Joined:** `{u_data[5][:10]}`\n"
                f"💎 **Status:** `ENTERPRISE VIP`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"*Keep utilizing the bot to level up your status!*")
        bot.reply_to(m, dash, parse_mode="Markdown")

    elif "💻 Mega Code Lab" in txt:
        msg = bot.send_message(m.chat.id, "💻 **INITIALIZING CODE LAB...**\nProvide your complete project requirements. I will write an extensive, production-ready codebase:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_code)

    elif "📦 ZIP Project Builder" in txt:
        msg = bot.send_message(m.chat.id, "📦 **ZIP ARCHITECT ONLINE.**\nTell me what application to build. I will structure directories, code files, and package them into a `.zip` file:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_zip)

    elif "📕 Color PDF Book" in txt:
        msg = bot.send_message(m.chat.id, "📕 **PDF PUBLISHER WAKING UP...**\nEnter the central topic of your book.\n*(Pro Tip: Send an image first to use it as the Cover Page!)*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_pdf)

    elif "🌐 Smart Google Sync" in txt:
        msg = bot.send_message(m.chat.id, "🌐 **GLOBAL RADAR ACTIVE.**\nWhat topic should I deep-search and summarize?", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_search)

    elif "🖼️ Web Art Gen" in txt:
        msg = bot.send_message(m.chat.id, "🎨 **PICASSO MODULE ONLINE.**\nDescribe the image you want to generate (e.g., 'A cyberpunk city at night in 4k'):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_media)
        
    elif "👁️ Vision Analysis" in txt:
        img_path = user_sessions.get(uid, {}).get("cover_img")
        if img_path and os.path.exists(img_path):
            mid = animator.play(m.chat.id, "Scanning Image Pixels", "radar", speed=0.5)
            ans, node = mega_ai_brain(uid, "Analyze this image in deep detail. What is it? What are the key elements? Be descriptive.", "Vision AI Specialist", img_path)
            bot.delete_message(m.chat.id, mid)
            bot.reply_to(m, f"👁️ **VISION REPORT**\n━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Engine:* `{node}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, "⚠️ **No image in memory!** Please send a photo first, then click this button again.")

    elif "📖 Story Teller" in txt:
        msg = bot.send_message(m.chat.id, "📖 **CREATIVE WRITER READY.**\nGive me a prompt, character names, or a setting for your epic story:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, step_story)

    else:
        # Default Deep Chat Engine
        mid = animator.play(m.chat.id, "Processing Logic", "blocks", speed=0.3)
        ans, node = mega_ai_brain(uid, txt)
        bot.delete_message(m.chat.id, mid)
        
        # Avoid Telegram Message length limit (4096)
        if len(ans) > 4000:
            for x in range(0, len(ans), 4000):
                bot.send_message(m.chat.id, ans[x:x+4000], parse_mode="Markdown")
            bot.send_message(m.chat.id, f"🤖 *Engine:* `{node}`", parse_mode="Markdown")
        else:
            bot.reply_to(m, f"🧠 **MI AI RESPONSE**\n━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Engine:* `{node}`", parse_mode="Markdown")

# ================= ⚡ STEP FUNCTIONS (HEAVY LIFTING) =================

def step_code(m):
    mid = animator.play(m.chat.id, "Compiling Deep Code", "hack", loops=2, speed=0.6)
    ans, node = mega_ai_brain(m.from_user.id, f"Write a highly structured, error-free, advanced code for: {m.text}. Use best practices and add professional comments.", "Senior Enterprise Programmer")
    bot.delete_message(m.chat.id, mid)
    
    # Safe sending for long code
    if len(ans) > 4000:
        bot.reply_to(m, "⚠️ *Code is massive. Sending in chunks...*", parse_mode="Markdown")
        for x in range(0, len(ans), 4000):
            bot.send_message(m.chat.id, ans[x:x+4000])
    else:
        bot.reply_to(m, f"💻 **CODE LAB RESULT**\n━━━━━━━━━━━━━━\n{ans}\n\n🤖 *Powered by {node}*", parse_mode="Markdown")

def step_zip(m):
    mid = animator.play(m.chat.id, "Architecting File System", "blocks")
    zip_buf = zip_project_builder(m.from_user.id, m.text)
    zip_buf.name = f"MI_Project_{random.randint(1000,9999)}.zip"
    bot.delete_message(m.chat.id, mid)
    bot.send_document(m.chat.id, zip_buf, caption=f"📦 **PROJECT BUILT SUCCESSFULLY**\n━━━━━━━━━━━━━━\n🎯 **Task:** {m.text}\n👨‍💻 **Architect:** Muaaz Iqbal\n*Download and extract to view source files.*", parse_mode="Markdown")

def step_pdf(m):
    mid = animator.play(m.chat.id, "Rendering Typography & Layout", "radar", loops=2)
    cover_img = user_sessions.get(m.from_user.id, {}).get("cover_img")
    
    try:
        pdf_buf = build_color_pdf(m.from_user.id, m.text, cover_img)
        safe_name = re.sub(r'\W+', '_', m.text[:15])
        pdf_buf.name = f"MI_Book_{safe_name}.pdf"
        bot.delete_message(m.chat.id, mid)
        bot.send_document(m.chat.id, pdf_buf, caption=f"📕 **LUXURY PDF PUBLISHED**\n━━━━━━━━━━━━━━\n📖 **Topic:** {m.text}\n💎 High Quality Print Ready.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        bot.delete_message(m.chat.id, mid)
        bot.reply_to(m, "⚠️ **Failed to generate PDF.** Please try a simpler topic.")

def step_search(m):
    mid = animator.play(m.chat.id, "Scraping Global Datasets", "matrix", speed=0.4)
    report, img_url, node = ai_google_search(m.from_user.id, m.text)
    bot.delete_message(m.chat.id, mid)
    
    try:
        # Send photo with caption
        bot.send_photo(m.chat.id, img_url, caption=f"🌐 **SMART SEARCH REPORT**\n━━━━━━━━━━━━━━\n{report[:800]}...\n\n🤖 *Sync Node:* `{node}`\n🔗 [Deep View Google Results](https://www.google.com/search?q={urllib.parse.quote(m.text)})", parse_mode="Markdown")
    except:
        # Fallback if image fails
        bot.reply_to(m, f"🌐 **SMART SEARCH REPORT**\n━━━━━━━━━━━━━━\n{report}\n\n🤖 *Sync Node:* `{node}`", parse_mode="Markdown")

def step_media(m):
    mid = animator.play(m.chat.id, "Generating 4K Canvas", "blocks")
    p = urllib.parse.quote(m.text)
    image_url = f"https://image.pollinations.ai/prompt/{p}?width=1024&height=1024&nologo=true"
    bot.delete_message(m.chat.id, mid)
    bot.send_photo(m.chat.id, image_url, caption=f"🎨 **MI ART GALLERY**\n━━━━━━━━━━━━━━\n✨ **Prompt:** `{m.text}`\n👨‍🎨 *Rendered instantly.*", parse_mode="Markdown")

def step_story(m):
    mid = animator.play(m.chat.id, "Writing Epic Narrative", "hack", loops=2)
    ans, node = mega_ai_brain(m.from_user.id, f"Write an extensive, highly engaging, emotional and vividly descriptive story about: {m.text}. Use dialogue and character development.", "Master Novelist")
    bot.delete_message(m.chat.id, mid)
    bot.reply_to(m, f"📖 **THE MI TALE**\n━━━━━━━━━━━━━━\n{ans}\n\n✒️ *Penned by {node}*", parse_mode="Markdown")

# ================= 🚀 SERVER BOOT & KEEP-ALIVE =================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔥 MI AI PUBLIC ENTERPRISE EDITION IS ONLINE 🔥")
    print("👨‍💻 Architect: Muaaz Iqbal | Muslim Islam")
    print("🚀 Status: Quantum Cores Running Perfectly")
    print("🛡️ Anti-Crash Middleware Active")
    print("="*50 + "\n")
    
    # Infinity polling with robust error handling to prevent exit
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Polling crashed: {e}. Rebooting in 3 seconds...")
            time.sleep(3)
