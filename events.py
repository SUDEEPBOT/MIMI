from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
# 🔥 'remove_group' import karna mat bhulna
from database import register_user, check_registered, get_logger_group, update_group_activity, remove_group

# --- 1. WELCOME USER & BOT ADD LOG ---
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user 
    
    # Group DB me Update/Insert karo
    try:
        update_group_activity(chat.id, chat.title)
    except: pass

    for member in update.message.new_chat_members:
        # 🤖 A. AGAR BOT ADD HUA
        if member.id == context.bot.id:
            await update.message.reply_text("😎 **Thanks for adding me!**\nMake me **Admin** to use full power! ⚡")
            
            # Logger Log
            logger_id = get_logger_group()
            if logger_id:
                txt = (
                    "🟢 **BOT ADDED TO NEW GROUP**\n\n"
                    f"📍 **Group:** {chat.title}\n"
                    f"🆔 **Group ID:** `{chat.id}`\n"
                    f"👤 **Added By:** {user.first_name} (@{user.username or 'NoUser'})\n"
                    f"🆔 **User ID:** `{user.id}`"
                )
                kb = [[InlineKeyboardButton("❌ Close", callback_data="close_log")]]
                try:
                    await context.bot.send_message(chat_id=logger_id, text=txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                except: pass
            continue
            
        # 👤 B. NORMAL USER
        if not check_registered(member.id):
            register_user(member.id, member.first_name)
        
        try:
            await update.message.reply_text(f"👋 **Welcome {member.first_name}!**\nWelcome to {update.effective_chat.title} ❤️")
        except: pass

# --- 2. TRACK LEAVE (BOT REMOVE & STATS FIX) ---
async def track_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_user = update.message.left_chat_member
    action_by = update.message.from_user 
    chat = update.effective_chat
    
    # 🤖 A. AGAR BOT NIKALA GAYA / LEFT HUA
    if left_user.id == context.bot.id:
        
        # 🔥 STEP 1: Database se Group Hatao (Taki Stats update ho)
        remove_group(chat.id)
        
        # 🔥 STEP 2: Logger me Bhejo
        logger_id = get_logger_group()
        if logger_id:
            txt = (
                "🔴 **BOT REMOVED / LEFT GC**\n\n"
                f"📍 **Group Name:** {chat.title}\n"
                f"🆔 **Group ID:** `{chat.id}`\n"
                f"👮 **Removed By:** {action_by.first_name} (@{action_by.username or 'NoUser'})\n"
                f"🆔 **Admin ID:** `{action_by.id}`"
            )
            kb = [[InlineKeyboardButton("❌ Close", callback_data="close_log")]]
            try:
                await context.bot.send_message(chat_id=logger_id, text=txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                print(f"Logger Error: {e}")
        return 

    # 👤 B. NORMAL USER LEFT (Ignored)
