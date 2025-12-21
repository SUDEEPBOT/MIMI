import html
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    get_balance, update_balance, get_bank_balance, 
    update_bank_balance, get_loan, set_loan, 
    users_col, is_dead, is_protected, get_user # 🔥 New Imports added
)

# Config
MAX_LOAN_LIMIT = 50000

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- 🔥 NEW /bal COMMAND ---
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows User Profile, Rank, Status & Balance"""
    user = update.effective_user
    uid = user.id
    
    # 1. Fetch Data
    wallet = get_balance(uid)
    bank = get_bank_balance(uid)
    total_amt = wallet + bank
    user_db = get_user(uid)
    kills = user_db.get("kills", 0) if user_db else 0
    
    # 2. Determine Status
    if is_dead(uid):
        status = "💀 DEAD"
    elif is_protected(uid):
        status = "🛡️ PROTECTED"
    else:
        status = "👤 ALIVE"

    # 3. Calculate Global Rank (Based on Wallet Balance)
    # Logic: Count users who have MORE money than current user + 1
    rank = users_col.count_documents({"balance": {"$gt": wallet}}) + 1

    # 4. Message Formatting
    msg = f"""
<blockquote><b>👤 {to_fancy("USER PROFILE")}</b></blockquote>

<blockquote>
<b>📛 ɴᴀᴍᴇ :</b> {html.escape(user.first_name)}
<b>💰 ᴛᴏᴛᴀʟ :</b> ₹{total_amt}
<b>🏆 ʀᴀɴᴋ :</b> #{rank}
<b>❤️ sᴛᴀᴛᴜs :</b> {status}
<b>⚔️ ᴋɪʟʟs :</b> {kills}
</blockquote>

<blockquote>
<b>👛 ᴡᴀʟʟᴇᴛ :</b> ₹{wallet}
<b>💎 ʙᴀɴᴋ :</b> ₹{bank}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- OLD COMMANDS (Deposit/Withdraw/Loan) ---
# Ye commands same rahenge bas /bal upar naya add kiya hai

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wallet = get_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/deposit 100</code> or <code>/deposit all</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all":
        amount = wallet
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Please enter a valid number.")

    if amount <= 0: return await update.message.reply_text("❌ Amount must be greater than 0.")
    if amount > wallet: return await update.message.reply_text("❌ Insufficient funds in wallet!")
    
    update_balance(user.id, -amount)
    update_bank_balance(user.id, amount)
    new_bank = get_bank_balance(user.id)
    
    msg = f"<blockquote><b>✅ {to_fancy('DEPOSIT SUCCESS')}</b></blockquote>\n<blockquote><b>💰 ᴅᴇᴘᴏsɪᴛᴇᴅ :</b> ₹{amount}\n<b>💎 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ :</b> ₹{new_bank}</blockquote>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bank = get_bank_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/withdraw 100</code> or <code>/withdraw all</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all":
        amount = bank
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Please enter a valid number.")

    if amount <= 0: return await update.message.reply_text("❌ Amount must be greater than 0.")
    if amount > bank: return await update.message.reply_text("❌ Insufficient funds in Bank!")
    
    update_bank_balance(user.id, -amount)
    update_balance(user.id, amount)
    new_wallet = get_balance(user.id)
    
    msg = f"<blockquote><b>✅ {to_fancy('WITHDRAW SUCCESS')}</b></blockquote>\n<blockquote><b>💸 ᴡɪᴛʜᴅʀᴇᴡ :</b> ₹{amount}\n<b>👛 ɴᴇᴡ ᴡᴀʟʟᴇᴛ :</b> ₹{new_wallet}</blockquote>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def take_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_loan = get_loan(user.id)
    
    if current_loan > 0:
        return await update.message.reply_text(f"❌ You already have an active loan of <b>₹{current_loan}</b>!", parse_mode=ParseMode.HTML)
        
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/loan 5000</code>", parse_mode=ParseMode.HTML)
    
    if amount > MAX_LOAN_LIMIT:
        return await update.message.reply_text(f"❌ Limit Exceeded! Max Loan: <b>₹{MAX_LOAN_LIMIT}</b>", parse_mode=ParseMode.HTML)
    
    update_balance(user.id, amount)
    set_loan(user.id, amount)
    
    msg = f"<blockquote><b>💸 {to_fancy('LOAN APPROVED')}</b></blockquote>\n<blockquote><b>💰 ᴀᴍᴏᴜɴᴛ :</b> ₹{amount}\n<b>⚠️ ɴᴏᴛᴇ :</b> Repay this soon!</blockquote>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def repay_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    debt = get_loan(user.id)
    wallet = get_balance(user.id)
    
    if debt == 0: return await update.message.reply_text("✅ You have no active loans.")
    
    amount_to_pay = debt
    if wallet < debt:
        return await update.message.reply_text(f"❌ You need <b>₹{debt}</b>. You have <b>₹{wallet}</b>.", parse_mode=ParseMode.HTML)
        
    update_balance(user.id, -amount_to_pay)
    set_loan(user.id, 0)
    
    msg = f"<blockquote><b>✅ {to_fancy('LOAN REPAID')}</b></blockquote>\n<blockquote><b>💸 ᴘᴀɪᴅ :</b> ₹{amount_to_pay}\n<b>🔓 sᴛᴀᴛᴜs :</b> Debt Free</blockquote>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
