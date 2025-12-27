import asyncio
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode, ChatAction

# Imports
from tools.controller import process_stream
from tools.stream import play_stream
from tools.database import get_cached_song, save_cached_song 
from tools.downloader import download # ✅ Downloader zaroori hai
from tools.stream import worker_app # VC Join ke liye
from config import OWNER_NAME, INSTAGRAM_LINK

# --- HELPER: PROGRESS BAR ---
def get_progress_bar(duration):
    try:
        bar = "◉—————————" 
        return f"{bar}"
    except:
        return "◉—————————"

# --- FPLAY COMMAND (/fplay) ---
async def fplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    try: await update.message.delete()
    except: pass

    if not context.args:
        temp = await context.bot.send_message(chat.id, "<blockquote>❌ <b>Usage:</b> /fplay [Song Name]</blockquote>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(3)
        try: await temp.delete()
        except: pass
        return

    query = " ".join(context.args)
    
    status_msg = await context.bot.send_message(
        chat.id,
        f"<blockquote>⚡ <b>Fast Searching...</b>\n<code>{query}</code></blockquote>", 
        parse_mode=ParseMode.HTML
    )

    # --- 🚀 STEP 1: CHECK DATABASE (CACHE) ---
    cached_data = await get_cached_song(query)

    file_path = None
    title = None
    duration = None
    thumbnail = None
    link = None
    
    # Flag to track if we found in cache
    found_in_cache = False

    if cached_data:
        # ✅ CACHE HIT
        await status_msg.edit_text(f"<blockquote>🚀 <b>Found in Cache! Downloading...</b></blockquote>", parse_mode=ParseMode.HTML)
        
        title = cached_data["title"]
        duration = cached_data["duration"]
        thumbnail = cached_data["thumbnail"]
        link = cached_data["link"]
        
        # 🔥 CRITICAL FIX: Link se File Download karo
        file_path = await download(link)
        
        if file_path:
            found_in_cache = True
        else:
            await status_msg.edit_text("❌ Cache File Expired. Searching Web...")
            # Agar download fail hua (link expire), to normal search pe jao
            found_in_cache = False

    # --- 🐢 STEP 2: CACHE MISS (NORMAL SEARCH) ---
    if not found_in_cache:
        await status_msg.edit_text(f"<blockquote>🔍 <b>Searching Web...</b>\n<code>{query}</code></blockquote>", parse_mode=ParseMode.HTML)
        
        # Controller call karo (Search + Download)
        error, data = await process_stream(chat.id, user.first_name, query)
        
        if error:
            return await status_msg.edit_text(error)
            
        # Data set karo
        title = data["title"]
        duration = data["duration"]
        thumbnail = data["thumbnail"]
        link = data["link"]
        # Note: process_stream already play_stream call kar chuka hai, 
        # isliye humein niche dubara call karne ki zaroorat nahi hai agar ye step chala to.
        
        # 🔥 SAVE TO CACHE
        cache_entry = {
            "title": title,
            "duration": duration,
            "thumbnail": thumbnail,
            "link": link
        }
        await save_cached_song(query, cache_entry)
        
        # Message delete kardo kyunki process_stream ne apna message bhej diya hoga
        try: await status_msg.delete()
        except: pass
        return

    # --- 🎵 STEP 3: PLAY (ONLY IF FROM CACHE) ---
    # Agar Cache se aaya tha, to ab humein manually play_stream call karna padega
    
    # VC Check Fix
    try:
        invite_link = await context.bot.export_chat_invite_link(chat.id)
        await worker_app.join_chat(invite_link)
    except: pass # Errors handled inside play_stream
    
    # Play
    safe_title = html.escape(title)
    safe_user = html.escape(user.first_name)
    
    success, position = await play_stream(chat.id, file_path, safe_title, duration, safe_user, link, thumbnail)
    
    # --- MESSAGE UI (Buttons) ---
    if success:
        # Playing Message
        bar_display = get_progress_bar(duration)
        buttons = [
            [InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")],
            [InlineKeyboardButton("II", callback_data="music_pause"), InlineKeyboardButton("▶", callback_data="music_resume"), InlineKeyboardButton("‣‣I", callback_data="music_skip"), InlineKeyboardButton("▢", callback_data="music_stop")],
            [InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link), InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)],
            [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
        ]
        
        caption = f"""
<blockquote><b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ (Fast)</b></blockquote>

<blockquote><b>🫀ᴛɪᴛʟᴇ :</b> <a href="{link}">{safe_title}</a>
<b>🍁 ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>🫧 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {safe_user}</blockquote>
<blockquote><b>🍫ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
        await context.bot.send_photo(chat.id, photo=thumbnail, caption=caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    
    elif position is not None:
        # Queued Message
        caption = f"""
<blockquote><b>📝 ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ</b></blockquote>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{safe_title}</a>
<b>🍫 ᴘᴏsɪᴛɪᴏɴ :</b> <code>#{position}</code>
<b>🍁 ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>🫧 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {safe_user}</blockquote>
"""
        await context.bot.send_photo(chat.id, photo=thumbnail, caption=caption, parse_mode=ParseMode.HTML)

    # Cleanup status msg
    try: await status_msg.delete()
    except: pass


def register_handlers(app):
    app.add_handler(CommandHandler(["fplay", "fp"], fplay_command))
    print("  ✅ Fast-Play Module Loaded!")

