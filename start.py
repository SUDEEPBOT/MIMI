from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import check_registered
from config import DEFAULT_BANNER, OWNER_ID 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # --- 1. AGAR REGISTER NAHI HAI ---
    if not check_registered(user.id):
        kb = [[InlineKeyboardButton("📝 Register Now (Get ₹500)", callback_data=f"reg_start_{user.id}")]]
        await update.message.reply_text(
            f"🛑 **Account Not Found!**\n\n"
            f"Hi **{user.first_name}**! 👋\n"
            f"Game khelne aur Paise kamane ke liye Register karein.\n\n"
            f"💰 **Bonus:** ₹500 Free!",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # --- 2. REGISTERED USER (Full Render + Group Offer) ---
    
    caption = (
        f"👋 **Welcome Back, {user.first_name}!**\n\n"
        f"🤑 **LOOT OFFER:**\n"
        f"Mujhe apne Group me add karo aur paao **₹1000 Instant!** 💸\n\n"
        f"🎮 **Menu:**\n"
        f"💣 **Mines:** `/bet 100`\n"
        f"🔫 **Crime:** `/rob` `/kill`\n"
        f"🛒 **Shop:** `/shop`\n\n"
        f"👇 **Niche click karke group me add karo!**"
    )

    # Smart Link jo user ko add karne bhejega
    bot_username = context.bot.username
    keyboard = [
        [InlineKeyboardButton("➕ Add Me to Group (Get ₹1000) ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("🚑 Support / Owner", url=f"tg://user?id={OWNER_ID}")]
    ]

    # Photo Bhejo
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=DEFAULT_BANNER,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        # Fallback agar photo fail ho
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        
