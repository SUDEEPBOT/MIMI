from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import check_registered
from config import OWNER_ID

# --- CONFIG ---
# Tumhari Image ka Direct Link (Yahi link use karna)
START_IMG = "https://i.ibb.co/WLB2B31/1000007092.png" 

# --- MAIN START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot_name = context.bot.first_name
    bot_username = context.bot.username

    # 1. CHECK REGISTRATION
    if not check_registered(user.id):
        kb = [[InlineKeyboardButton("📝 Register Now (Get ₹500)", callback_data=f"reg_start_{user.id}")]]
        await update.message.reply_photo(
            photo=START_IMG,
            caption=(
                f"🛑 **Account Not Found!**\n\n"
                f"Hey **{user.first_name}**! 👋\n"
                f"Looks like you are new here.\n"
                f"Join the game to earn money, rob friends & chat with AI!\n\n"
                f"💰 **Register Bonus:** ₹500 Free!"
            ),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # 2. REGISTERED USER (MAIN MENU)
    caption = (
        f"👋 **Hey {user.first_name}!**\n"
        f"I am **{bot_name}** 🤖\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌟 **The Advanced AI & Economy Bot**\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 **Play Games** | 💰 **Earn Money**\n"
        f"🔫 **Rob & Kill** | 🗣️ **Chat with AI**\n\n"
        f"👇 **Click buttons below to explore:**"
    )

    keyboard = [
        [
            InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"),
            InlineKeyboardButton("🚑 Support", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("📚 Help & Menu", callback_data="help_main")
        ],
        [
            InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ]

    await update.message.reply_photo(
        photo=START_IMG,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# --- CALLBACK HANDLER (MENU LOGIC) ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user = update.effective_user
    
    # 1. HELP MAIN MENU
    if data == "help_main":
        caption = (
            f"📚 **MAIN MENU**\n"
            f"Select a category to see commands:\n\n"
            f"🏦 **Bank:** Deposit, Withdraw, Loans\n"
            f"📈 **Market:** Invest, Sell, Ranking\n"
            f"🎮 **Games:** Mines, Betting\n"
            f"🛒 **Shop:** Buy VIP, Items"
        )
        kb = [
            [InlineKeyboardButton("🏦 Bank", callback_data="help_bank"), InlineKeyboardButton("📈 Market", callback_data="help_market")],
            [InlineKeyboardButton("🎮 Games", callback_data="help_games"), InlineKeyboardButton("🛒 Shop", callback_data="help_shop")],
            [InlineKeyboardButton("➡️ Next Page", callback_data="help_next")],
            [InlineKeyboardButton("🔙 Back Home", callback_data="back_home")]
        ]
        # Photo wahi rahegi, bas caption aur buttons badlenge
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 2. SUB MENUS
    elif data == "help_bank":
        text = (
            "🏦 **BANKING SYSTEM**\n\n"
            "• `/balance` - Check wallet\n"
            "• `/bank` - Check bank account\n"
            "• `/deposit [amount]` - Save money\n"
            "• `/withdraw [amount]` - Get cash\n"
            "• `/loan` - Take loan\n"
            "• `/payloan` - Repay loan"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_market":
        text = (
            "📈 **STOCK MARKET**\n\n"
            "• `/market` - View Share Prices\n"
            "• `/invest [group_id] [amount]` - Buy Shares\n"
            "• `/sell [group_id]` - Sell Shares\n"
            "• `/ranking` - Top Groups"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_games":
        text = (
            "🎮 **GAMES & CASINO**\n\n"
            "• `/bet [amount]` - Play Mines 💣\n"
            "• `/rob` - Rob someone (Reply)\n"
            "• `/kill` - Kill someone (Reply)\n"
            "• `/pay [amount]` - Give money"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    
    elif data == "help_shop":
        text = (
            "🛒 **VIP SHOP**\n\n"
            "• `/shop` - Open Shop Menu\n"
            "• `/redeem [code]` - Get Free Money\n"
            "• `/protect` - Buy Shield (24h)"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "help_next":
        text = (
            "🔮 **EXTRA COMMANDS**\n\n"
            "• `/top` - Global Leaderboard\n"
            "• `/alive` - Check Health\n"
            "• `/eco` - Economy Status\n"
            "• `Hi Yuki` - Chat with AI"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="help_main")]]
        await q.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    # 3. START CHAT (AI)
    elif data == "start_chat_ai":
        await q.answer("💬 AI Mode Active!", show_alert=False)
        await q.message.reply_text(f"Hey **{user.first_name}**! 👋\nBas **'Hi Yuki'** ya **'Hello'** likho, main turant reply karungi!")

    # 4. BACK HOME
    elif data == "back_home":
        # Wapis main menu
        caption = (
            f"👋 **Hey {user.first_name}!**\n"
            f"I am **{context.bot.first_name}** 🤖\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌟 **The Advanced AI & Economy Bot**\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"🎮 **Play Games** | 💰 **Earn Money**\n"
            f"🔫 **Rob & Kill** | 🗣️ **Chat with AI**\n\n"
            f"👇 **Click buttons below to explore:**"
        )
        keyboard = [
            [InlineKeyboardButton("💬 Chat AI", callback_data="start_chat_ai"), InlineKeyboardButton("🚑 Support", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"), InlineKeyboardButton("📚 Help & Menu", callback_data="help_main")],
            [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]
        await q.edit_message_caption(caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        
