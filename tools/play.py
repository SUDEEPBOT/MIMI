import uuid
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from config import MONGO_DB_URI, BOT_NAME, ASSISTANT_ID # Config check kar lena
from tools.stream import play_stream # Tumhare stream logic se connect kiya

# --- PLAY COMMAND ---
async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    message = update.message
    
    if not context.args:
        text = f"<blockquote><b>❌ Incorrect Usage</b></blockquote>\n\n<b>Usage:</b> <code>/play [Song Name]</code>"
        return await message.reply_text(text, parse_mode=ParseMode.HTML)

    song_name = " ".join(context.args)
    status_msg = await message.reply_text(f"<blockquote><b>🔍 Searching...</b></blockquote>\n<code>{song_name}</code>", parse_mode=ParseMode.HTML)

    try:
        # --- STEP 1: ASSISTANT PRESENCE CHECK ---
        try:
            assistant_member = await chat.get_member(int(ASSISTANT_ID))
            # Agar Assistant Ban hai
            if assistant_member.status in ["kicked", "banned"]:
                keyboard = [[InlineKeyboardButton("✅ Unban Assistant", callback_data=f"unban_assist_{ASSISTANT_ID}")]]
                return await status_msg.edit_text(
                    f"<blockquote><b>❌ Assistant Banned</b></blockquote>\nAssistant is banned in <b>{chat.title}</b>.\n\nClick below to unban!",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode=ParseMode.HTML
                )
        except Exception:
            # Assistant Group mein nahi hai, toh join karwane ka try karenge
            try:
                invite_link = await context.bot.export_chat_invite_link(chat.id)
                # Hum Assistant (Userbot) ko bolenge join karne ko (via stream logic)
                from tools.stream import worker 
                await worker.join_chat(invite_link)
            except Exception as e:
                return await status_msg.edit_text(
                    f"<blockquote><b>❌ Assistant Missing</b></blockquote>\nMake me <b>Admin</b> with <b>Invite Users</b> permission so I can bring the assistant!",
                    parse_mode=ParseMode.HTML
                )

        # --- STEP 2: PLAY LOGIC ---
        # Yahan hum tumhare stream.py ke play_stream function ko call kar rahe hain
        from tools.stream import play_stream
        # Maan lete hain tumhare paas download logic hai jo file_path deta hai
        # Abhi ke liye hum direct stream logic handle kar rahe hain
        
        success, result = await play_stream(chat.id, song_name, song_name, 0, user.first_name)

        if success:
            success_text = f"""
<blockquote><b>✅ Playing Started</b></blockquote>

<b>🎶 Title :</b> {song_name}
<b>👤 Requested By :</b> {user.first_name}
<b>✨ Status :</b> <code>Streaming...</code>
"""
            await status_msg.edit_text(success_text, parse_mode=ParseMode.HTML)
        else:
            await status_msg.edit_text(f"<blockquote><b>⌛ Added to Queue</b></blockquote>\nPosition: <code>{result}</code>", parse_mode=ParseMode.HTML)

    except Exception as e:
        await status_msg.edit_text(f"<blockquote><b>❌ Play Error</b></blockquote>\n<code>{str(e)}</code>", parse_mode=ParseMode.HTML)

# --- CALLBACK FOR UNBAN BUTTON ---
async def unban_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    data = query.data

    if data.startswith("unban_assist_"):
        # Admin Check
        user_member = await chat.get_member(query.from_user.id)
        if user_member.status not in ["administrator", "creator"]:
            return await query.answer("❌ Only Admins can unban!", show_alert=True)

        try:
            await chat.unban_member(int(ASSISTANT_ID))
            await query.answer("✅ Assistant Unbanned!", show_alert=True)
            await query.edit_message_text(
                "<blockquote><b>✅ Assistant Unbanned</b></blockquote>\nThanks for unbanning! You can now use <code>/play</code> again.",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await query.answer(f"❌ Error: {e}", show_alert=True)

# --- REGISTER HANDLERS ---
def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_music))
    app.add_handler(CallbackQueryHandler(unban_button_click, pattern="^unban_assist_"))
    
