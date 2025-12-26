from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode, ChatAction
import time
import asyncio

# Import hamara Naya Controller aur Engine
from tools.controller import process_stream
from tools.stream import stop_stream, pause_stream, resume_stream, skip_stream
from config import OWNER_NAME, BOT_NAME

# ✅ Import buttons module
from tools.buttons import (
    stream_markup_timer,
    stream_markup,
    track_markup,
    playlist_markup,
    livestream_markup,
    slider_markup
)

# --- AUTO DELETE HELPER FUNCTION ---
async def auto_delete_message(context, chat_id, message_id, delay=5):
    """Message ko automatically delete karne ka function"""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# --- THUMBNAIL VALIDATION HELPER ---
def validate_thumbnail_url(url):
    """Thumbnail URL ko validate aur fix karo"""
    if not url or url == "" or url == "None" or url is None:
        return None
    
    # Check if it's a valid URL
    if url.startswith(('http://', 'https://')):
        return url
    
    return None

# --- PLAY COMMAND (/play) ---
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # ✅ USER KI /play COMMAND KO DELETE KARO (Spam protection)
    try:
        await update.message.delete()
    except:
        pass
    
    if not context.args:
        # Usage message bhejo aur delete ho jaye
        msg = await update.message.reply_text(
            "❌ **Usage:** `/play [Song Name or Link]`", 
            parse_mode=ParseMode.MARKDOWN
        )
        # 5 seconds baad delete
        context.job_queue.run_once(
            lambda ctx: auto_delete_message(ctx, chat.id, msg.message_id, 5),
            when=5
        )
        return

    query = " ".join(context.args)
    
    # ✅ SEARCHING MESSAGE - Auto delete wala
    status_msg = await update.message.reply_text(
        f"🔎 **Searching:** `{query}`...", 
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Auto delete ka job schedule karo
    context.job_queue.run_once(
        lambda ctx: auto_delete_message(ctx, chat.id, status_msg.message_id, 5),
        when=5
    )
    
    await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

    # Controller se data le aao
    error, data = await process_stream(chat.id, user.first_name, query)

    if error:
        # Error message bhi auto delete ho
        await status_msg.edit_text(error)
        context.job_queue.run_once(
            lambda ctx: auto_delete_message(ctx, chat.id, status_msg.message_id, 5),
            when=5
        )
        return

    title = data.get("title", "Unknown Title")
    duration = data.get("duration", "0:00")
    thumbnail = data.get("thumbnail", None)
    requested_by = data.get("user", user.first_name)
    link = data.get("link", "#")
    videoid = data.get("videoid", "unknown")
    
    # ✅ THUMBNAIL VALIDATION
    valid_thumbnail = validate_thumbnail_url(thumbnail)
    
    # ✅ BUTTONS.PY का USE करें
    # Track selection buttons
    buttons = track_markup(
        _={},  # Empty dict for default strings
        videoid=videoid,
        user_id=user.id,
        channel="group",
        fplay=False
    )
    
    markup = InlineKeyboardMarkup(buttons)

    if data.get("status") is True:
        text = f"""
<blockquote><b>🎵 Streaming Started</b></blockquote>

<blockquote>
<b>📌 Title:</b> <a href="{link}">{title}</a>
<b>⏱ Duration:</b> <code>{duration}</code>
<b>🎧 Audio Quality:</b> <code>128 kbps</code>
<b>👤 Requested By:</b> {requested_by}
<b>🕐 Playing Since:</b> <code>{time.strftime('%H:%M:%S')}</code>
</blockquote>

<blockquote>━━━━━━━━━━━━━━━━━━</blockquote>

<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
        # Searching message delete karo
        try:
            await status_msg.delete()
        except:
            pass
        
        # Player buttons के साथ message भेजें
        player_buttons = stream_markup_timer(
            _={},
            chat_id=chat.id,
            played="0:00",
            dur=duration
        )
        
        player_markup = InlineKeyboardMarkup(player_buttons)
        
        # Main result message bhejo - WITH OR WITHOUT PHOTO
        if valid_thumbnail:
            try:
                result_msg = await context.bot.send_photo(
                    chat.id, 
                    photo=valid_thumbnail, 
                    caption=text, 
                    reply_markup=markup,  # Track selection buttons
                    parse_mode=ParseMode.HTML,
                    has_spoiler=True
                )
            except Exception as photo_error:
                print(f"⚠️ Photo send error, sending text only: {photo_error}")
                # Fallback to text message
                result_msg = await context.bot.send_message(
                    chat.id,
                    text=text,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
        else:
            # No thumbnail, send text only
            result_msg = await context.bot.send_message(
                chat.id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        
        # Player control message अलग से
        player_msg = await context.bot.send_message(
            chat.id,
            text="🎛 **Player Controls**",
            reply_markup=player_markup
        )

    elif data.get("status") is False:
        position = data.get("position", 1)
        text = f"""
<blockquote><b>📝 Added to Queue</b></blockquote>

<blockquote>
<b>📌 Title:</b> <a href="{link}">{title}</a>
<b>🔢 Position:</b> <code>#{position}</code>
<b>⏱ Duration:</b> <code>{duration}</code>
<b>👤 Requested By:</b> {requested_by}
<b>🕐 Requested At:</b> <code>{time.strftime('%H:%M:%S')}</code>
</blockquote>

<blockquote>━━━━━━━━━━━━━━━━━━</blockquote>

<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
        # Searching message delete karo
        try:
            await status_msg.delete()
        except:
            pass
        
        # Result message bhejo - WITH OR WITHOUT PHOTO
        if valid_thumbnail:
            try:
                result_msg = await context.bot.send_photo(
                    chat.id, 
                    photo=valid_thumbnail, 
                    caption=text, 
                    reply_markup=markup, 
                    parse_mode=ParseMode.HTML,
                    has_spoiler=True
                )
            except Exception as photo_error:
                print(f"⚠️ Photo send error: {photo_error}")
                result_msg = await context.bot.send_message(
                    chat.id,
                    text=text,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
        else:
            result_msg = await context.bot.send_message(
                chat.id,
                text=text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
    
    else:
        error_msg = "❌ **Error:** Assistant VC join nahi kar paya."
        await status_msg.edit_text(error_msg)
        # Error message bhi delete ho jaye
        context.job_queue.run_once(
            lambda ctx: auto_delete_message(ctx, chat.id, status_msg.message_id, 5),
            when=5
        )

# --- CALLBACK QUERY HANDLER (Buttons.py के callbacks handle करें) ---
async def music_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("ADMIN"):
        # ADMIN commands handle करें
        parts = data.split("|")
        if len(parts) >= 3:
            action = parts[1]
            chat_id = parts[2]
            
            response_text = ""
            
            if action == "Pause":
                success = await pause_stream(int(chat_id))
                response_text = f"⏸ **Paused** by {query.from_user.first_name}" if success else "❌ Failed to pause"
                
            elif action == "Resume":
                success = await resume_stream(int(chat_id))
                response_text = f"▶️ **Resumed** by {query.from_user.first_name}" if success else "❌ Failed to resume"
                
            elif action == "Skip":
                success, _ = await skip_stream(int(chat_id))
                response_text = f"⏭ **Skipped** by {query.from_user.first_name}" if success else "❌ Failed to skip"
                
            elif action == "Stop":
                success = await stop_stream(int(chat_id))
                response_text = f"⏹ **Stopped** by {query.from_user.first_name}" if success else "❌ Failed to stop"
            
            # Edit message aur delete job schedule karo
            await query.edit_message_text(response_text)
            
            # Response ko bhi 3 seconds baad delete karo
            context.job_queue.run_once(
                lambda ctx: ctx.bot.delete_message(
                    chat_id=query.message.chat_id, 
                    message_id=query.message.message_id
                ) if hasattr(ctx, 'bot') else None,
                when=3
            )
    
    elif data.startswith("MusicStream"):
        # Audio/Video stream selection
        await query.edit_message_text("🎵 Stream selection processed...")
        # Ye bhi delete ho jaye
        context.job_queue.run_once(
            lambda ctx: ctx.bot.delete_message(
                chat_id=query.message.chat_id, 
                message_id=query.message.message_id
            ) if hasattr(ctx, 'bot') else None,
            when=3
        )
    
    elif data == "close":
        try:
            await query.message.delete()
        except:
            pass
    
    elif data.startswith("forceclose"):
        try:
            await query.message.delete()
        except:
            pass

# --- OTHER COMMANDS (Ye bhi auto delete) ---
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User ki command delete karo
    try:
        await update.message.delete()
    except:
        pass
    
    chat_id = update.effective_chat.id
    success = await stop_stream(chat_id)
    
    if success:
        text = f"""
<blockquote><b>⏹ Music Stopped</b></blockquote>
<blockquote>Queue cleared by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
        msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        # 5 seconds baad delete
        context.job_queue.run_once(
            lambda ctx: auto_delete_message(ctx, chat_id, msg.message_id, 5),
            when=5
        )
    else:
        msg = await update.message.reply_text("❌ Nothing is playing.")
        context.job_queue.run_once(
            lambda ctx: auto_delete_message(ctx, chat_id, msg.message_id, 5),
            when=5
        )

async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass
    
    chat_id = update.effective_chat.id
    success = await pause_stream(chat_id)
    
    if success:
        text = f"""
<blockquote><b>⏸ Playback Paused</b></blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    else:
        text = "❌ Failed to pause playback"
        
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML if success else None)
    context.job_queue.run_once(
        lambda ctx: auto_delete_message(ctx, chat_id, msg.message_id, 5),
        when=5
    )

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass
    
    chat_id = update.effective_chat.id
    success = await resume_stream(chat_id)
    
    if success:
        text = f"""
<blockquote><b>▶️ Playback Resumed</b></blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    else:
        text = "❌ Failed to resume playback"
        
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML if success else None)
    context.job_queue.run_once(
        lambda ctx: auto_delete_message(ctx, chat_id, msg.message_id, 5),
        when=5
    )

async def skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass
    
    chat_id = update.effective_chat.id
    success, next_song = await skip_stream(chat_id)
    
    if success and next_song:
        text = f"""
<blockquote><b>⏭ Song Skipped</b></blockquote>
<blockquote>Now playing: {next_song.get('title', 'Next Song')}</blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    elif success:
        text = f"""
<blockquote><b>⏭ Song Skipped</b></blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    else:
        text = "❌ Failed to skip or queue is empty"
    
    msg = await update.message.reply_text(
        text, 
        parse_mode=ParseMode.HTML if success else None
    )
    context.job_queue.run_once(
        lambda ctx: auto_delete_message(ctx, chat_id, msg.message_id, 5),
        when=5
    )

# --- 🔌 AUTO LOADER REGISTER FUNCTION ---
def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_command))
    app.add_handler(CommandHandler(["stop", "end"], stop_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler(["skip", "next"], skip_command))
    
    # ✅ CALLBACK HANDLER ADD करें
    app.add_handler(CallbackQueryHandler(music_callback_handler, pattern="^(ADMIN|MusicStream|close|forceclose|slider|GetTimer)"))
    
    print("  ✅ Music Module Loaded with Auto-Delete Feature")
