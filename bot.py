# ================== MI AI ULTRA BOT ==================
import telebot
import requests
import os
from telebot import types
from fpdf import FPDF
import zipfile
import time

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# ================== MEMORY ==================
memory = {}

def get_history(uid):
    return memory.get(uid, [])

def save_history(uid, hist):
    memory[uid] = hist[-10:]

# ================== AI ENGINES ==================

# ---- GROQ ----
def ask_groq(history):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        messages = []
        for h in history:
            role = "assistant" if h["role"] == "model" else "user"
            messages.append({"role": role, "content": h["text"]})

        res = requests.post(url,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": messages
            }, timeout=15
        )

        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"], "Groq"

    except:
        pass

    return None, None


# ---- GEMINI ----
def ask_gemini(history):
    try:
        text = "\n".join([h["text"] for h in history])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        res = requests.post(url, json={
            "contents": [{"parts":[{"text": text}]}]
        }, timeout=15)

        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"

    except:
        pass

    return None, None


# ---- OPENROUTER ----
def ask_openrouter(history):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        messages = []
        for h in history:
            role = "assistant" if h["role"] == "model" else "user"
            messages.append({"role": role, "content": h["text"]})

        res = requests.post(url,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": messages
            }, timeout=15
        )

        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"], "OpenRouter"

    except:
        pass

    return None, None


# ================== SMART ROUTER ==================
def mi_ai(history):
    engines = [ask_groq, ask_gemini, ask_openrouter]

    for eng in engines:
        reply, name = eng(history)
        if reply:
            return reply, name

    return "⚠️ All AI servers busy", "None"


# ================== IMAGE ==================
def gen_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}?nologo=true"

# ================== VIDEO ==================
def gen_video(prompt):
    return f"https://pollinations.ai/p/{prompt}?model=video"

# ================== PDF ==================
def create_pdf(text, filename="book.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf.output(filename)
    return filename

# ================== ZIP ==================
def create_zip(name, code):
    zname = f"{name}.zip"

    with zipfile.ZipFile(zname, 'w') as z:
        z.writestr("main.py", code)
        z.writestr("README.md", f"# {name}")
        z.writestr("requirements.txt", "requests\ntelebot\nfpdf")

    return zname

# ================== UI ==================
def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💬 Chat", "🎨 Image", "🎥 Video")
    kb.add("📘 PDF", "📦 Build", "🧹 Clear")
    return kb

# ================== START ==================
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🚀 MI AI ULTRA ACTIVE", reply_markup=menu())

# ================== COMMANDS ==================

@bot.message_handler(commands=['draw'])
def draw(m):
    prompt = m.text.replace("/draw", "")
    bot.send_photo(m.chat.id, gen_image(prompt))

@bot.message_handler(commands=['video'])
def video(m):
    prompt = m.text.replace("/video", "")
    bot.send_message(m.chat.id, gen_video(prompt))

@bot.message_handler(commands=['pdf'])
def pdf(m):
    topic = m.text.replace("/pdf", "")
    text, _ = mi_ai([{"role":"user","text":f"Write full book on {topic}"}])

    file = create_pdf(text)
    bot.send_document(m.chat.id, open(file,'rb'))

@bot.message_handler(commands=['build'])
def build(m):
    name = m.text.replace("/build", "")
    code, _ = mi_ai([{"role":"user","text":f"Create python project {name}"}])

    zipf = create_zip(name, code)
    bot.send_document(m.chat.id, open(zipf,'rb'))

# ================== VOICE ==================
@bot.message_handler(content_types=['voice'])
def voice(m):
    file = bot.get_file(m.voice.file_id)
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

    audio = requests.get(url).content

    res = requests.post(
        "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        data=audio
    )

    text = res.json().get("text","")

    reply, model = mi_ai([{"role":"user","text":text}])
    bot.reply_to(m, f"{reply}\n[{model}]")

# ================== PHOTO ==================
@bot.message_handler(content_types=['photo'])
def photo(m):
    bot.reply_to(m, "👁️ Vision upgrade coming (Groq Vision add kar sakte hain)")

# ================== CHAT ==================
@bot.message_handler(func=lambda m: True)
def chat(m):
    uid = str(m.from_user.id)
    hist = get_history(uid)

    hist.append({"role":"user","text":m.text})

    reply, model = mi_ai(hist)

    hist.append({"role":"model","text":reply})
    save_history(uid, hist)

    bot.reply_to(m, f"{reply}\n\n[{model}]")

# ================== RUN ==================
print("🔥 MI AI ULTRA RUNNING")
bot.infinity_polling()