from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import users_col

async def user_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Sabse bada Killer dhoondo (Jiske kills sabse zyada hain)
    # Taaki hum usse special tag de sakein
    top_killer_data = users_col.find_one(sort=[("kills", -1)])
    top_killer_id = top_killer_data["_id"] if top_killer_data else None

    # 2. Top 10 Ameer Log (Rich List)
    top_users = users_col.find().sort("balance", -1).limit(10)
    
    msg = "🏆 **GLOBAL RICH LIST** 🏆\n\n"
    rank = 1
    
    for user in top_users:
        name = user.get("name", "Unknown")
        bal = user.get("balance", 0)
        titles = user.get("titles", [])
        kills = user.get("kills", 0) # Kill Count
        user_id = user.get("_id")
        
        # Rank Icons
        if rank == 1: icon = "🥇"
        elif rank == 2: icon = "🥈"
        elif rank == 3: icon = "🥉"
        else: icon = f"{rank}."
        
        # --- TAGS LOGIC ---
        tags = ""
        
        # A. Shop Title (Sirf pehla wala dikhayenge)
        if titles:
            tags += f" [{titles[0]}]"
            
        # B. KILLER TAG (Agar ye banda Top Killer hai aur kills > 0 hai)
        if user_id == top_killer_id and kills > 0:
            tags += " 🔪[THE KILLER]"

        # --- FORMATTING LOGIC ---
        # Rule: Rank 1 WALA hamesha Blockquote me hoga
        # Aur jinke paas Titles hain wo bhi Blockquote me honge
        
        if rank == 1 or titles:
            # ✨ VIP Look (Blockquote)
            msg += f"> {icon} {name}{tags}\n> 💰 ₹{bal} | 💀 Kills: {kills}\n\n"
        else:
            # 👤 Normal Look
            msg += f"{icon} {name}{tags} — ₹{bal} (💀 {kills})\n"
            
        rank += 1
        
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    
