from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 **COMMAND LIST**\n\n"
        "🎮 **GAME:**\n"
        "`/bet <amount>` - Play Game (e.g. /bet 100)\n"
        "`/balance` - Check Paisa\n\n"
        
        "📈 **MARKET:**\n"
        "`/ranking` - Top Groups\n"
        "`/market` - Share Price\n"
        "`/invest <amount>` - Invest Karo\n"
        "`/sell` - Profit Book Karo\n\n"
        
        "🛒 **SHOP & EXTRAS:**\n"
        "`/shop` - VIP Titles\n"
        "`/top` - Leaderboard\n"
        "`/redeem <code>` - Promo Code\n\n"
        
        "🔐 **ADMIN ONLY:**\n"
        "`/addkey <key>` - Add API Key\n"
        "`/delkey <key>` - Remove API Key\n"
        "`/keys` - Count Keys\n"
        "`/cast <msg>` - Broadcast\n"
        "`/code <name> <amt> <limit>` - Create Code\n"
        "`/add <id> <money>` - Give Money"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
