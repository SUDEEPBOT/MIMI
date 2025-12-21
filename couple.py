import os
import random
import io
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database import users_col

# --- CONFIGURATION (इन्हें इमेज के हिसाब से सेट किया है) ---
BG_IMAGE = "ccpic.png" 
FONT_PATH = "arial.ttf" 

# 🔥 COORDINATES FIXED FOR RED BACKGROUND
# (Left aur Right circle ka Top-Left corner X, Y)
# Agar thoda idhar udhar ho to numbers badal kar adjust kar lena
POS_1 = (165, 205)   # Left Circle (Ladka)
POS_2 = (660, 205)   # Right Circle (Ladki)
CIRCLE_SIZE = 360    # Circle ka size bada kiya hai taki fit aaye

def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- IMAGE GENERATOR ---
async def make_couple_img(user1, user2, context):
    try:
        bg = Image.open(BG_IMAGE).convert("RGBA")
    except:
        return None 

    # Helper function to get Circular PFP
    async def get_pfp(u_id):
        try:
            # Telegram se photo fetch karo
            photos = await context.bot.get_profile_photos(u_id, limit=1)
            
            if photos.total_count > 0:
                # Photo download karo
                file = await context.bot.get_file(photos.photos[0][-1].file_id)
                f_data = await file.download_as_bytearray()
                img = Image.open(io.BytesIO(f_data)).convert("RGBA")
            else:
                # Agar photo nahi hai to Default letters
                img = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (255, 200, 200))

            # Resize High Quality
            img = ImageOps.fit(img, (CIRCLE_SIZE, CIRCLE_SIZE), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

            # Circular Mask Create Karo
            mask = Image.new('L', (CIRCLE_SIZE, CIRCLE_SIZE), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, CIRCLE_SIZE, CIRCLE_SIZE), fill=255)

            # Mask Apply Karo
            result = Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (0, 0, 0, 0))
            result.paste(img, (0, 0), mask=mask)
            return result
            
        except Exception as e:
            print(f"PFP Error: {e}")
            # Error aane par blank circle
            return Image.new('RGBA', (CIRCLE_SIZE, CIRCLE_SIZE), (128, 128, 128))

    # 1. Get PFPs
    pfp1 = await get_pfp(user1['id'])
    pfp2 = await get_pfp(user2['id'])

    # 2. Paste on Background (Mask ke sath taaki transparency rahe)
    bg.paste(pfp1, POS_1, pfp1)
    bg.paste(pfp2, POS_2, pfp2)

    # 3. Add Text
    draw = ImageDraw.Draw(bg)
    try:
        # Font size thoda chhota kiya hai taki naam fit aaye
        font = ImageFont.truetype(FONT_PATH, 35) 
    except:
        font = ImageFont.load_default()

    # Name 1 (Left)
    name1 = user1['first_name'][:15]
    bbox1 = draw.textbbox((0, 0), name1, font=font)
    w1 = bbox1[2] - bbox1[0]
    # Center text below circle
    x1 = POS_1[0] + (CIRCLE_SIZE - w1) // 2
    y1 = POS_1[1] + CIRCLE_SIZE + 40 # Thoda aur neeche
    draw.text((x1, y1), name1, font=font, fill=(255, 255, 255)) # White Text better dikhega red par

    # Name 2 (Right)
    name2 = user2['first_name'][:15]
    bbox2 = draw.textbbox((0, 0), name2, font=font)
    w2 = bbox2[2] - bbox2[0]
    x2 = POS_2[0] + (CIRCLE_SIZE - w2) // 2
    y2 = POS_2[1] + CIRCLE_SIZE + 40
    draw.text((x2, y2), name2, font=font, fill=(255, 255, 255)) 

    # 4. Save
    bio = io.BytesIO()
    bio.name = "couple.png"
    bg.save(bio, "PNG")
    bio.seek(0)
    return bio

# --- COUPLE COMMAND ---
async def couple_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    bot_id = context.bot.id 
    
    msg = await update.message.reply_text("🔍 **Finding a perfect match...**", parse_mode=ParseMode.MARKDOWN)

    try:
        # 🔥 FIX: Exclude Bot ID from selection
        pipeline = [
            {"$match": {"_id": {"$ne": bot_id}}}, # Bot ko list se hata diya
            {"$sample": {"size": 2}}
        ]
        
        random_users = list(users_col.aggregate(pipeline))
        
        # Agar DB me users kam hain to fake data for testing
        if len(random_users) < 2:
            # Fallback (Agar DB khali hai to ye use hoga)
            u1 = {'_id': update.effective_user.id, 'name': update.effective_user.first_name}
            u2 = {'_id': 0, 'name': 'Herobrine'} # Dummy
        else:
            u1 = random_users[0]
            u2 = random_users[1]
        
        # Prepare Data
        user1_data = {'id': u1['_id'], 'first_name': u1.get('name', 'Lover 1')}
        user2_data = {'id': u2['_id'], 'first_name': u2.get('name', 'Lover 2')}
        
    except Exception as e:
        print(e)
        return await msg.edit_text("❌ Database Error.")

    # Generate Image
    photo = await make_couple_img(user1_data, user2_data, context)
    
    if not photo:
        await msg.edit_text("❌ Error: `ccpic.png` nahi mili ya corrupt hai.")
        return

    # Caption
    caption = f"""
<blockquote><b>💘 {to_fancy("TODAY'S COUPLE")}</b></blockquote>

<blockquote>
<b>🦁 ʙᴏʏ :</b> {html.escape(user1_data['first_name'])}
<b>🐰 ɢɪʀʟ :</b> {html.escape(user2_data['first_name'])}
</blockquote>

<blockquote>
<b>✨ ᴍᴀᴛᴄʜ :</b> 100% ❤️
<b>📅 ᴅᴀᴛᴇ :</b> {to_fancy("FOREVER")}
</blockquote>
"""
    # Support Button
    kb = [[InlineKeyboardButton("👨‍💻 Support", url="https://t.me/Dev_Digan")]] 
    
    await update.message.reply_photo(
        photo=photo,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML
    )
    await msg.delete()
