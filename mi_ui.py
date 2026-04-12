from telebot import types
import random

# --- MI AI BRANDING & CONFIG ---
BOT_NAME = "MI AI"
DEVELOPER = "Muaaz Iqbal"
# Aapka Diya Hua Image Link
BANNER_URL = "https://i.ibb.co/992tM2jb/file-0000000090007208b1864eebb1423b3e.png"

def get_main_keyboard(uid, role, ADMIN_ID, db):
    """MI AI Neural Interface - Crafted by Muaaz Iqbal"""
    u = db.get_user(uid)
    deep = u.get("deep_think", 0)

    kb = types.InlineKeyboardMarkup(row_width=2)

    # Section 1: Core Intelligence
    kb.add(
        types.InlineKeyboardButton("🧠 Neural Chat",    callback_data="ask_ai"),
        types.InlineKeyboardButton("🔍 Web Vision",    callback_data="mode_search"),
    )
    
    # Section 2: Tools & Analytics
    kb.add(
        types.InlineKeyboardButton("⚡ Engine Hub",    callback_data="menu_engines"),
        types.InlineKeyboardButton("📊 Analytics",      callback_data="view_dashboard"),
    )
    
    # Section 3: Modes
    kb.add(
        types.InlineKeyboardButton("💬 Conversation",  callback_data="set_mode_chat"),
        types.InlineKeyboardButton("📚 Study Pro",     callback_data="set_mode_study"),
    )
    
    # Section 4: Creativity (IMG GENERATE)
    deep_status = "🔵 ON" if deep else "⚪ OFF"
    kb.add(
        types.InlineKeyboardButton("🎨 IMG GENERATE",  callback_data="gen"),
        types.InlineKeyboardButton(f"🧠 Deep Think: {deep_status}", callback_data="toggle_deep"),
    )
    
    # Section 5: Memory & Profile
    kb.add(
        types.InlineKeyboardButton("🗑️ Clear Brain",   callback_data="clear_memory"),
        types.InlineKeyboardButton("👤 My Profile",    callback_data="my_profile"),
    )
    
    # Section 6: About & Identity
    kb.add(types.InlineKeyboardButton("ℹ️ About MI AI", callback_data="about_bot"))
    
    # Admin Section
    if role == "admin" or uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("🛡️ SYSTEM ADMIN PANEL", callback_data="admin_panel"))

    return kb
