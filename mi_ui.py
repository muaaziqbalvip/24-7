from telebot import types
import random

# --- BRANDING SETTINGS ---
BOT_NAME = "MI AI"
DEVELOPER = "Muaaz Iqbal"
BANNER_URL = "https://image.pollinations.ai/prompt/cyberpunk%20robotic%20brain%20neon%20lighting%20ultra%20hd?width=1024&height=512&nologo=true"

def get_main_keyboard(uid, role, ADMIN_ID, db):
    """MI AI Neural Control Panel — Styled by Muaaz Iqbal"""
    u = db.get_user(uid)
    deep = u.get("deep_think", 0)

    kb = types.InlineKeyboardMarkup(row_width=2)

    # Row 1 — Primary Core
    kb.add(
        types.InlineKeyboardButton("🧠 Neural Chat",    callback_data="ask_ai"),
        types.InlineKeyboardButton("🔍 Web Search",    callback_data="mode_search"),
    )
    # Row 2 — System Settings
    kb.add(
        types.InlineKeyboardButton("⚙️ Engine Hub",    callback_data="menu_engines"),
        types.InlineKeyboardButton("📊 Dashboard",      callback_data="view_dashboard"),
    )
    # Row 3 — Interaction Modes
    kb.add(
        types.InlineKeyboardButton("💬 Chat Mode",     callback_data="set_mode_chat"),
        types.InlineKeyboardButton("📚 Study Mode",    callback_data="set_mode_study"),
    )
    # Row 4 — Creative & Memory
    deep_status = "🔵 ON" if deep else "⚪ OFF"
    kb.add(
        types.InlineKeyboardButton("🎨 IMG GENERATE",  callback_data="gen"),
        types.InlineKeyboardButton(f"🧠 Deep: {deep_status}", callback_data="toggle_deep"),
    )
    # Row 5 — User & System
    kb.add(
        types.InlineKeyboardButton("🗑️ Clear Memory",   callback_data="clear_memory"),
        types.InlineKeyboardButton("👤 My Profile",    callback_data="my_profile"),
    )
    # Row 6 — Info
    kb.add(types.InlineKeyboardButton("ℹ️ About MI AI", callback_data="about_bot"))
    
    # Row 7 — Admin
    if role == "admin" or uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("🛡️ ADMIN PANEL", callback_data="admin_panel"))

    return kb

def get_engine_keyboard(current_engine):
    """Engine selection panel."""
    def mark(e):
        return f"✅ {e.upper()}" if current_engine == e else e.upper()

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton(f"🤖 {mark('auto')} (Recommended)",   callback_data="set_eng_auto"),
        types.InlineKeyboardButton(f"💎 {mark('gemini')} 1.5 Flash",     callback_data="set_eng_gemini"),
        types.InlineKeyboardButton(f"⚡ {mark('groq')} LLaMA-3.3",      callback_data="set_eng_groq"),
        types.InlineKeyboardButton("🔙 Back to Menu",                     callback_data="go_home"),
    )
    return kb
