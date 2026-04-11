import requests
from config import GEMINI, GROQ, OPENROUTER

def gemini(history):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI}"
        r = requests.post(url, json={"contents": history}, timeout=10)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
    except:
        pass
    return None, None

def groq(history):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        msgs = [{"role":"user" if h["role"]=="user" else "assistant","content":h["parts"][0]["text"]} for h in history]

        r = requests.post(url,
            headers={"Authorization": f"Bearer {GROQ}"},
            json={"model":"llama3-70b-8192","messages":msgs},
            timeout=10)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], "Groq"
    except:
        pass
    return None, None

def openrouter(history):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        msgs = [{"role":"user" if h["role"]=="user" else "assistant","content":h["parts"][0]["text"]} for h in history]

        r = requests.post(url,
            headers={"Authorization": f"Bearer {OPENROUTER}"},
            json={"model":"openai/gpt-3.5-turbo","messages":msgs},
            timeout=10)

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"], "OpenRouter"
    except:
        pass
    return None, None

def ask_ai(history, mode="fast"):
    engines = [gemini, groq, openrouter] if mode=="pro" else [gemini, openrouter, groq]

    for fn in engines:
        res, name = fn(history)
        if res:
            return res, name

    return "⚠️ All AI busy", "None"