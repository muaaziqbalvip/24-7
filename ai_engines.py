import requests
import os

GEMINI = os.getenv("GEMINI_API_KEY")
GROQ = os.getenv("GROQ_API_KEY")
OPENROUTER = os.getenv("OPENROUTER_API_KEY")

# -------- GEMINI --------
def gemini(history):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI}"
        r = requests.post(url, json={"contents": history}, timeout=10)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
    except:
        pass
    return None, None

# -------- GROQ --------
def groq(history):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        msgs = [{"role": "user" if h["role"]=="user" else "assistant", "content": h["parts"][0]["text"]} for h in history]

        r = requests.post(url,
            headers={"Authorization": f"Bearer {GROQ}"},
            json={"model":"llama3-70b-8192","messages":msgs},
            timeout=10)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], "Groq"
    except:
        pass
    return None, None

# -------- OPENROUTER --------
def openrouter(history):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        msgs = [{"role": "user" if h["role"]=="user" else "assistant", "content": h["parts"][0]["text"]} for h in history]

        r = requests.post(url,
            headers={"Authorization": f"Bearer {OPENROUTER}"},
            json={"model":"openai/gpt-3.5-turbo","messages":msgs},
            timeout=10)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], "OpenRouter"
    except:
        pass
    return None, None

# -------- ROUTER --------
def ask_all(history):
    for fn in [gemini, groq, openrouter]:
        reply, name = fn(history)
        if reply:
            return reply, name
    return "⚠️ All AI busy", "None"