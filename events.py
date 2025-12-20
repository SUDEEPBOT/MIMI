from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import register_user, check_registered, get_logger_group, update_group_activity

# --- 1. WELCOME USER & BOT ADD LOG ---
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user # Jo message bhej raha hai (Add karne wala)
    
    # Group Activity Update (Agar group.py me ye function nahi hai to yaha rehne do)
    try:
        update_group_activity(chat.id, chat.title)
    except: pass

    for member in update.message.new_chat_members:
        # 🤖 A. AGAR BOT KHUD ADD HUA HAI (SIRF ISKA LOG JAYEGA)
        if member.id == context.bot.id:
            await update.message.reply_text("😎 **Thanks for adding me!**\nMake me **Admin** to use full power! ⚡")
            
            # Logger Group me bhejo
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
                except Exception as e:
                    print(f"Logger Error: {e}")
            continue
            
        # 👤 B. NORMAL USER JOIN (SIRF DATABASE UPDATE, NO LOG)
        if not check_registered(member.id):
            register_user(member.id, member.first_name)
        
        # Welcome Message (Group me dikhega, Logger me nahi jayega)
        try:
            await update.message.reply_text(f"👋 **Welcome {member.first_name}!**\nWelcome to {update.effective_chat.title} ❤️")
        except: pass

# --- 2. TRACK LEAVE/KICK (ONLY BOT LOGS) ---
async def track_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_user = update.message.left_chat_member
    action_by = update.message.from_user # Jisne nikala (ya khud nikla)
    chat = update.effective_chat
    
    # Logger ID check karo
    logger_id = get_logger_group()
    
    # 🤖 A. AGAR BOT KO NIKALA GAYA (SIRF ISKA LOG JAYEGA)
    if left_user.id == context.bot.id:
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
            except: pass
        return 

    # 👤 B. NORMAL USER LEFT - (KOI LOG NAHI JAYEGA)
