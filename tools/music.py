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

    title = data["title"]
    duration = data["duration"]
    thumbnail = data["thumbnail"]
    requested_by = data["user"]
    link = data["link"]
    videoid = data.get("videoid", "unknown")
    
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

    if data["status"] is True:
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
        
        # Main result message bhejo
        result_msg = await context.bot.send_photo(
            chat.id, 
            photo=thumbnail, 
            caption=text, 
            reply_markup=markup,  # Track selection buttons
            parse_mode=ParseMode.HTML,
            has_spoiler=True
        )
        
        # Player control message अलग से
        player_msg = await context.bot.send_message(
            chat.id,
            text="🎛 **Player Controls**",
            reply_markup=player_markup
        )
        
        # ✅ RESULT MESSAGES KO BHI AUTO DELETE KARNE KA OPTION
        # (Optional: Agar aap chahte hain ki result bhi delete ho, toh ye uncomment karo)
        # context.job_queue.run_once(
        #     lambda ctx: auto_delete_message(ctx, chat.id, result_msg.message_id, 30),
        #     when=30
        # )
        # context.job_queue.run_once(
        #     lambda ctx: auto_delete_message(ctx, chat.id, player_msg.message_id, 30),
        #     when=30
        # )

    elif data["status"] is False:
        position = data["position"]
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
        
        # Result message bhejo
        result_msg = await context.bot.send_photo(
            chat.id, 
            photo=thumbnail, 
            caption=text, 
            reply_markup=markup, 
            parse_mode=ParseMode.HTML,
            has_spoiler=True
        )
        
        # ✅ Queue message bhi auto delete kar sakte hain (Optional)
        # context.job_queue.run_once(
        #     lambda ctx: auto_delete_message(ctx, chat.id, result_msg.message_id, 10),
        #     when=10
        # )
    
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
        _, action, chat_id = data.split("|")
        
        # Button click ke response ko bhi auto delete karo
        response_text = ""
        
        if action == "Pause":
            await pause_stream(int(chat_id))
            response_text = f"⏸ **Paused** by {query.from_user.first_name}"
            
        elif action == "Resume":
            await resume_stream(int(chat_id))
            response_text = f"▶️ **Resumed** by {query.from_user.first_name}"
            
        elif action == "Skip":
            await skip_stream(int(chat_id))
            response_text = f"⏭ **Skipped** by {query.from_user.first_name}"
            
        elif action == "Stop":
            await stop_stream(int(chat_id))
            response_text = f"⏹ **Stopped** by {query.from_user.first_name}"
        
        # Edit message aur delete job schedule karo
        await query.edit_message_text(response_text)
        
        # Response ko bhi 3 seconds baad delete karo
        context.job_queue.run_once(
            lambda ctx: ctx.bot.delete_message(
                chat_id=query.message.chat_id, 
                message_id=query.message.message_id
            ),
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
            ),
            when=3
        )
    
    elif data == "close":
        await query.message.delete()
    
    elif data.startswith("forceclose"):
        await query.message.delete()

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
    await pause_stream(chat_id)
    text = f"""
<blockquote><b>⏸ Playback Paused</b></blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
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
    await resume_stream(chat_id)
    text = f"""
<blockquote><b>▶️ Playback Resumed</b></blockquote>
<blockquote>Action by {update.effective_user.first_name}</blockquote>
<blockquote>✨ Powered by <b>{OWNER_NAME}</b></blockquote>
"""
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
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
