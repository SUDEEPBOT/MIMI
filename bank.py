import html
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import (
    get_balance, update_balance, get_bank_balance, 
    update_bank_balance, get_loan, set_loan, 
    users_col, is_dead, is_protected, get_user
)

# Config
MAX_LOAN_LIMIT = 50000

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- 1. CHECK BALANCE (/bal) - FIXED GAP ---
async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows User Profile, Rank, Status & Balance"""
    user = update.effective_user
    uid = user.id
    
    # Fetch Data
    wallet = get_balance(uid)
    bank = get_bank_balance(uid)
    total_amt = wallet + bank
    user_db = get_user(uid)
    kills = user_db.get("kills", 0) if user_db else 0
    
    # Determine Status
    if is_dead(uid): status = "💀 DEAD"
    elif is_protected(uid): status = "🛡️ PROTECTED"
    else: status = "👤 ALIVE"

    # Calculate Rank
    rank = users_col.count_documents({"balance": {"$gt": wallet}}) + 1

    # 🔥 FIX: Removed extra newlines between blockquotes
    msg = (
        f"<blockquote><b>👤 {to_fancy('USER PROFILE')}</b></blockquote>"
        f"<blockquote><b>📛 ɴᴀᴍᴇ :</b> {html.escape(user.first_name)}\n"
        f"<b>💰 ᴛᴏᴛᴀʟ :</b> ₹{total_amt}\n"
        f"<b>🏆 ʀᴀɴᴋ :</b> #{rank}\n"
        f"<b>❤️ sᴛᴀᴛᴜs :</b> {status}\n"
        f"<b>⚔️ ᴋɪʟʟs :</b> {kills}</blockquote>"
        f"<blockquote><b>👛 ᴡᴀʟʟᴇᴛ :</b> ₹{wallet}\n"
        f"<b>💎 ʙᴀɴᴋ :</b> ₹{bank}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. BANK INFO ---
async def bank_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_balance(update, context)

# --- 3. DEPOSIT ---
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    wallet = get_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/deposit 100</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all": amount = wallet
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Invalid number.")

    if amount <= 0: return await update.message.reply_text("❌ > 0 required.")
    if amount > wallet: return await update.message.reply_text("❌ Insufficient funds.")
    
    update_balance(user.id, -amount)
    update_bank_balance(user.id, amount)
    new_bank = get_bank_balance(user.id)
    
    msg = (
        f"<blockquote><b>✅ {to_fancy('DEPOSIT SUCCESS')}</b></blockquote>"
        f"<blockquote><b>💰 ᴅᴇᴘᴏsɪᴛᴇᴅ :</b> ₹{amount}\n"
        f"<b>💎 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ :</b> ₹{new_bank}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 4. WITHDRAW ---
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bank = get_bank_balance(user.id)
    
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/withdraw 100</code>", parse_mode=ParseMode.HTML)
    
    if context.args[0].lower() == "all": amount = bank
    else:
        try: amount = int(context.args[0])
        except: return await update.message.reply_text("❌ Invalid number.")

    if amount <= 0: return await update.message.reply_text("❌ > 0 required.")
    if amount > bank: return await update.message.reply_text("❌ Insufficient funds.")
    
    update_bank_balance(user.id, -amount)
    update_balance(user.id, amount)
    new_wallet = get_balance(user.id)
    
    msg = (
        f"<blockquote><b>✅ {to_fancy('WITHDRAW SUCCESS')}</b></blockquote>"
        f"<blockquote><b>💸 ᴡɪᴛʜᴅʀᴇᴡ :</b> ₹{amount}\n"
        f"<b>👛 ɴᴇᴡ ᴡᴀʟʟᴇᴛ :</b> ₹{new_wallet}</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 5. LOAN ---
async def take_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    current_loan = get_loan(user.id)
    
    if current_loan > 0: return await update.message.reply_text(f"❌ Pending Loan: <b>₹{current_loan}</b>", parse_mode=ParseMode.HTML)
        
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/loan 5000</code>", parse_mode=ParseMode.HTML)
    
    if amount > MAX_LOAN_LIMIT: return await update.message.reply_text(f"❌ Max Limit: <b>₹{MAX_LOAN_LIMIT}</b>", parse_mode=ParseMode.HTML)
    
    update_balance(user.id, amount)
    set_loan(user.id, amount)
    
    msg = (
        f"<blockquote><b>💸 {to_fancy('LOAN APPROVED')}</b></blockquote>"
        f"<blockquote><b>💰 ᴀᴍᴏᴜɴᴛ :</b> ₹{amount}\n"
        f"<b>⚠️ ɴᴏᴛᴇ :</b> Repay soon!</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 6. REPAY LOAN ---
async def repay_loan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    debt = get_loan(user.id)
    wallet = get_balance(user.id)
    
    if debt == 0: return await update.message.reply_text("✅ No active loans.")
    
    if wallet < debt: return await update.message.reply_text(f"❌ Need <b>₹{debt}</b>, have <b>₹{wallet}</b>.", parse_mode=ParseMode.HTML)
        
    update_balance(user.id, -debt)
    set_loan(user.id, 0)
    
    msg = (
        f"<blockquote><b>✅ {to_fancy('LOAN REPAID')}</b></blockquote>"
        f"<blockquote><b>💸 ᴘᴀɪᴅ :</b> ₹{debt}\n"
        f"<b>🔓 sᴛᴀᴛᴜs :</b> Debt Free</blockquote>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
