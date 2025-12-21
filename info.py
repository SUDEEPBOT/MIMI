import html
import random
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import users_col, chat_stats_col, get_balance, get_user

# Fancy Font Helper
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- PROGRESS BAR GENERATOR ---
def make_bar(percentage):
    filled = int(percentage / 10)
    empty = 10 - filled
    return "❤️" * filled + "🤍" * empty

# --- 1. USER INFO COMMAND ---
async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Determine Target (Reply or Self)
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        target = update.effective_user

    chat_id = update.effective_chat.id
    uid = target.id

    # 1. Fetch Telegram Details (Bio, Username, Photo)
    try:
        chat_info = await context.bot.get_chat(uid)
        bio = chat_info.bio if chat_info.bio else "No Bio Available"
    except:
        bio = "Private Profile"

    username = f"@{target.username}" if target.username else "No Username"
    
    # 2. Fetch Database Details
    wallet = get_balance(uid)
    
    # Global Rank Calculation
    rank = users_col.count_documents({"balance": {"$gt": wallet}}) + 1
    
    # Group Message Count
    stats = chat_stats_col.find_one({"group_id": chat_id, "user_id": uid})
    msgs = stats.get("overall", 0) if stats else 0
    
    # 3. Construct Message
    msg = f"""
<blockquote><b>👤 {to_fancy("USER INFORMATION")}</b></blockquote>

<blockquote>
<b>📛 ɴᴀᴍᴇ :</b> {html.escape(target.first_name)}
<b>🆔 ᴜsᴇʀ ɪᴅ :</b> <code>{uid}</code>
<b>📧 ᴜsᴇʀɴᴀᴍᴇ :</b> {username}
<b>📜 ʙɪᴏ :</b> {html.escape(bio)}
</blockquote>

<blockquote>
<b>🏆 ɢʟᴏʙᴀʟ ʀᴀɴᴋ :</b> #{rank}
<b>📨 ɢʀᴏᴜᴘ ᴍsɢs :</b> {msgs}
<b>💰 ᴡᴀʟʟᴇᴛ :</b> ₹{wallet}
</blockquote>
"""

    # 4. Send Photo or Text
    try:
        # Get Profile Photo
        photos = await target.get_profile_photos(limit=1)
        if photos.total_count > 0:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=msg,
                parse_mode=ParseMode.HTML
            )
        else:
            # If no photo, send text
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. LOVE CALCULATOR ---
async def love_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to someone to calculate love! ❤️")

    user1 = update.effective_user
    user2 = update.message.reply_to_message.from_user
    
    if user1.id == user2.id:
        return await update.message.reply_text("💔 You cannot love yourself!")

    # Calculate Love % (Random but seeded so it stays same for same pair for a while)
    # Using IDs to make it consistent (optional, currently purely random for fun)
    percentage = random.randint(0, 100)
    
    if percentage < 30: text = "💔 Toxic Couple"
    elif percentage < 60: text = "😐 Just Friends"
    elif percentage < 90: text = "❤️ Lovers"
    else: text = "💍 Soulmates!"

    bar = make_bar(percentage)

    msg = f"""
<blockquote><b>💘 {to_fancy("LOVE CALCULATOR")}</b></blockquote>

<blockquote>
<b>👤 {html.escape(user1.first_name)}</b>
       <b>+</b>
<b>👤 {html.escape(user2.first_name)}</b>
</blockquote>

<blockquote>
<b>💟 sᴄᴏʀᴇ :</b> {percentage}%
{bar}

<b>🏷 ʀᴇsᴜʟᴛ :</b> {text}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 3. STUPID METER ---
async def stupid_meter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        target = update.effective_user

    percentage = random.randint(0, 100)
    
    if percentage < 20: comment = "🧠 Einstein Level!"
    elif percentage < 50: comment = "🤓 Smart Enough."
    elif percentage < 80: comment = "🤪 Thoda Pagal."
    else: comment = "🥔 Total Potato!"

    msg = f"""
<blockquote><b>🥴 {to_fancy("STUPIDITY METER")}</b></blockquote>

<blockquote>
<b>👤 ᴛᴀʀɢᴇᴛ :</b> {html.escape(target.first_name)}
<b>📉 ʟᴇᴠᴇʟ :</b> {percentage}%
<b>💬 ᴄᴏᴍᴍᴇɴᴛ :</b> {comment}
</blockquote>
"""
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
