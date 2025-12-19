from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import wipe_database, set_economy_status, get_economy_status

# --- ECONOMY TOGGLE (/eco) ---
async def economy_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Economy System ko ON ya OFF karta hai"""
    # Security Check
    if update.effective_user.id != OWNER_ID: return
    
    # Current status check karke ulta kar do (Toggle)
    current = get_economy_status()
    new_status = not current
    set_economy_status(new_status)
    
    status_text = "🟢 **ON (Active)**" if new_status else "🔴 **OFF (Paused)**"
    
    await update.message.reply_text(
        f"⚙️ **ECONOMY SYSTEM UPDATE**\n\n"
        f"Status: {status_text}\n"
        f"Effect: Ab users Pay/Rob/Kill {'kar' if new_status else 'nahi kar'} payenge.",
        parse_mode=ParseMode.MARKDOWN
    )

# --- RESET MENU (/reset) ---
async def reset_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Database Wipe Warning Menu"""
    # Security Check
    if update.effective_user.id != OWNER_ID: return
    
    # Inline Buttons for Safety
    keyboard = [
        [InlineKeyboardButton("⚠️ YES, DELETE EVERYTHING ⚠️", callback_data="confirm_wipe")],
        [InlineKeyboardButton("❌ CANCEL", callback_data="cancel_wipe")]
    ]
    
    await update.message.reply_text(
        "☢️ **DANGER ZONE: DATABASE RESET** ☢️\n\n"
        "Kya aap sach me saara data delete karna chahte hain?\n"
        "👉 Users, Balance, Kills, Investments sab **ZERO** ho jayega.\n"
        "👉 Ye wapis **UNDO NAHI** ho sakta.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# --- CALLBACK HANDLER ---
async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Reset Buttons"""
    query = update.callback_query
    
    # Security Check (Koi aur button na daba de)
    if query.from_user.id != OWNER_ID: 
        await query.answer("Sirf Owner ye kar sakta hai! 😡", show_alert=True)
        return

    if query.data == "confirm_wipe":
        # Database Wipe Function Call
        wipe_database()
        
        await query.edit_message_text(
            "💀 **SYSTEM RESET SUCCESSFUL!**\n\n"
            "Sabka balance 0 ho gaya.\n"
            "Sare kills aur stats delete ho gaye.\n"
            "Nayi shuruwat karo! 🚀"
        )
    
    elif query.data == "cancel_wipe":
        await query.message.delete()
        await query.answer("Reset Cancelled! Bach gaye. 😮‍💨")
