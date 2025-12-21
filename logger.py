import time
import sys
import os
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import get_total_users, get_total_groups, get_all_voice_keys # 🔥 Voice Keys Import

# --- RESTART COMMAND ---
async def restart_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if str(user.id) != str(OWNER_ID): 
        return

    msg = await update.message.reply_text("🔄 **Restarting System...**")
    await time.sleep(2)
    await msg.edit_text("✅ **System Rebooted!**\nBack online in 5 seconds.")
    
    os.execl(sys.executable, sys.executable, *sys.argv)

# --- PING COMMAND (FIXED WITH CLOSE ACTION) ---
async def ping_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    # Loading Emoji
    msg = await update.message.reply_text("⚡")
    end_time = time.time()
    
    ping_ms = round((end_time - start_time) * 1000)
    
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        cpu = 0; ram = 0; disk = 0
    
    modules_list = [
        "Admin", "Bank", "Economy", "Games", "Market", 
        "Anti-Spam", "WordSeek", "Voice-AI", "Group Tools"
    ]
    modules_str = " | ".join(modules_list)
    
    # Direct Image Link
    PING_IMG = "https://i.ibb.co/QGGKVnw/image.png" 
    
    caption = f"""╭───〔 🤖 **sʏsᴛᴇᴍ sᴛᴀᴛᴜs** 〕───
┆
┆ ⚡ **ᴘɪɴɢ:** `{ping_ms}ms`
┆ 💻 **ᴄᴘᴜ:** `{cpu}%`
┆ 💾 **ʀᴀᴍ:** `{ram}%`
┆ 💿 **ᴅɪsᴋ:** `{disk}%`
┆
╰──────────────────────
📚 **ʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇs:**
`{modules_str}`"""

    # 🔥 CLOSE BUTTON (Make sure main.py handles 'close_ping')
    kb = [[InlineKeyboardButton("❌ Close", callback_data="close_ping")]]

    try:
        await msg.delete()
    except: pass
    
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=PING_IMG,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ **Image Error:** `{e}`\n\n{caption}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )

# --- STATS COMMAND (OWNER ONLY) ---
async def stats_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if str(user.id) != str(OWNER_ID): 
        return

    try:
        users = get_total_users()
        groups = get_total_groups()
        v_keys = len(get_all_voice_keys()) # Voice keys count
    except:
        users = 0; groups = 0; v_keys = 0

    text = f"""📊 **DATABASE & AI STATS**
    
👤 **Total Users:** `{users}`
👥 **Total Groups:** `{groups}`
🎙 **Voice Keys:** `{v_keys} Active`
    
⚡ **Server Status:** Running Smoothly
    """
    # Stats me bhi Close button de dete hain
    kb = [[InlineKeyboardButton("🗑 Close Stats", callback_data="close_log")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
