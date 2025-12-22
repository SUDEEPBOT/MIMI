import random
import string
import io
import html
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# --- WORD DATABASE ---
WORDS_POOL = [
    "LOVE", "FOREVER", "DIGAN", "PYTHON", "GAME", "FRIEND", 
    "COUPLE", "HEART", "MUSIC", "VIBE", "TRIBE", "INDIA",
    "BOT", "CODE", "HAPPY", "SMILE", "TRUST", "PEACE",
    "DREAM", "NIGHT", "PARTY", "MONEY", "POWER", "KING"
]

# --- GAME STORAGE ---
active_games = {}

# --- SETTINGS ---
GRID_SIZE = 8
CELL_SIZE = 60
FONT_PATH = "arial.ttf"

# Fancy Text Converter
def to_fancy(text):
    mapping = {'A': 'Λ', 'E': 'Є', 'S': 'δ', 'O': 'σ', 'T': 'ᴛ', 'N': 'ɴ', 'M': 'ᴍ', 'U': 'ᴜ', 'R': 'ʀ', 'D': 'ᴅ', 'C': 'ᴄ', 'P': 'ᴘ', 'G': 'ɢ', 'B': 'ʙ', 'L': 'ʟ', 'W': 'ᴡ', 'K': 'ᴋ', 'J': 'ᴊ', 'Y': 'ʏ', 'I': 'ɪ', 'H': 'ʜ'}
    return "".join(mapping.get(c.upper(), c) for c in text)

# --- HELPER: CREATE HINT ---
def create_hint(word):
    chars = list(word)
    num_to_hide = len(word) // 2 
    indices_to_hide = random.sample(range(len(word)), num_to_hide)
    for i in indices_to_hide:
        chars[i] = "＿"
    return " ".join(chars)

# --- 1. GENERATE GRID ---
def generate_grid():
    targets = random.sample(WORDS_POOL, 5)
    grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Store word positions for highlighting
    word_positions = {}
    
    for word in targets:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            direction = random.choice(['H', 'V']) 
            if direction == 'H':
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - len(word))
                if all(grid[row][col+i] == '' or grid[row][col+i] == word[i] for i in range(len(word))):
                    positions = []
                    for i in range(len(word)):
                        grid[row][col+i] = word[i]
                        positions.append((row, col+i))
                    word_positions[word] = {'direction': 'H', 'positions': positions}
                    placed = True
            else: 
                row = random.randint(0, GRID_SIZE - len(word))
                col = random.randint(0, GRID_SIZE - 1)
                if all(grid[row+i][col] == '' or grid[row+i][col] == word[i] for i in range(len(word))):
                    positions = []
                    for i in range(len(word)):
                        grid[row+i][col] = word[i]
                        positions.append((row+i, col))
                    word_positions[word] = {'direction': 'V', 'positions': positions}
                    placed = True
            attempts += 1
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == '': 
                grid[r][c] = random.choice(string.ascii_uppercase)
    
    return grid, targets, word_positions

# --- 2. DRAW IMAGE ---
def draw_grid_image(grid, found_words=None, word_positions=None):
    if found_words is None:
        found_words = []
    if word_positions is None:
        word_positions = {}
    
    width = GRID_SIZE * CELL_SIZE
    height = GRID_SIZE * CELL_SIZE + 60 
    img = Image.new('RGB', (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(FONT_PATH, 30)
        header_font = ImageFont.truetype(FONT_PATH, 40)
    except:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    # Draw header
    draw.rectangle([0, 0, width, 60], fill="#0088cc") 
    text = "WORD GRID"
    bbox = draw.textbbox((0, 0), text, font=header_font)
    w = bbox[2] - bbox[0]
    draw.text(((width - w)/2, 10), text, fill="white", font=header_font)
    
    # Draw grid with highlighting for found words
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x = c * CELL_SIZE
            y = r * CELL_SIZE + 60
            letter = grid[r][c]
            
            # Check if this cell belongs to a found word
            cell_in_found_word = False
            for word in found_words:
                if word in word_positions and (r, c) in word_positions[word]['positions']:
                    cell_in_found_word = True
                    break
            
            # Draw cell with different color if part of found word
            if cell_in_found_word:
                draw.rectangle([x, y, x+CELL_SIZE, y+CELL_SIZE], fill="#90EE90", outline="#4CAF50", width=2)
            else:
                draw.rectangle([x, y, x+CELL_SIZE, y+CELL_SIZE], outline="#dddddd", width=1)
            
            # Draw letter with strike-through if found
            bbox = draw.textbbox((0, 0), letter, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            
            if cell_in_found_word:
                # Draw letter in different color for found words
                draw.text((x + (CELL_SIZE-lw)/2, y + (CELL_SIZE-lh)/2), letter, fill="#2E7D32", font=font)
                # Draw diagonal line through the cell (X mark)
                draw.line([x+5, y+5, x+CELL_SIZE-5, y+CELL_SIZE-5], fill="#FF5722", width=3)
                draw.line([x+CELL_SIZE-5, y+5, x+5, y+CELL_SIZE-5], fill="#FF5722", width=3)
            else:
                draw.text((x + (CELL_SIZE-lw)/2, y + (CELL_SIZE-lh)/2), letter, fill="black", font=font)
    
    bio = io.BytesIO()
    img.save(bio, format="JPEG")
    bio.seek(0)
    return bio

# --- 3. START COMMAND ---
async def start_wordgrid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    grid, targets, word_positions = generate_grid()
    photo = draw_grid_image(grid, [], word_positions)
    hints = {word: create_hint(word) for word in targets}
    
    active_games[chat_id] = {
        'grid': grid, 
        'targets': targets, 
        'hints': hints, 
        'found': [],
        'word_positions': word_positions,
        'message_pinned': False
    }
    
    word_list_text = "\n".join([f"▫️ <code>{hints[w]}</code>" for w in targets])
    
    caption = f"""
<blockquote><b>🧩 {to_fancy("WORD GRID CHALLENGE")}</b></blockquote>

<blockquote>
{word_list_text}
</blockquote>

<blockquote>
<b>👇 Type the FULL word to solve!</b>
<b>👨‍💻 Dev:</b> Digan
<b>🎯 Found: 0/{len(targets)} words</b>
</blockquote>
"""
    kb = [[InlineKeyboardButton("🏳️ Give Up", callback_data="giveup_wordgrid")]]
    
    # Send the game message
    msg = await update.message.reply_photo(
        photo=photo,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML
    )
    
    active_games[chat_id]['msg_id'] = msg.message_id
    
    # Try to pin the message
    try:
        await msg.pin(disable_notification=True)
        active_games[chat_id]['message_pinned'] = True
    except Exception as e:
        print(f"Could not pin message: {e}")
        # Optional: Send a notification if pinning fails
        await update.message.reply_text("⚠️ Could not pin the game message. Make sure I have admin rights!", delete_after=5)

# --- 4. HANDLE GUESS ---
async def handle_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return
    
    chat_id = update.effective_chat.id
    text = update.message.text.upper().strip()
    
    if chat_id not in active_games:
        return
    
    game = active_games[chat_id]
    
    if text in game['targets'] and text not in game['found']:
        game['found'].append(text)
        
        # Update image with found word highlighted
        photo = draw_grid_image(game['grid'], game['found'], game['word_positions'])
        
        if len(game['found']) == len(game['targets']):
            # Game complete - unpin message and clean up
            if game.get('message_pinned'):
                try:
                    await context.bot.unpin_chat_message(chat_id=chat_id, message_id=game['msg_id'])
                except:
                    pass
            
            del active_games[chat_id]
            
            # Send final image with all words found
            final_caption = f"""
<blockquote><b>🏆 {to_fancy("GAME COMPLETE")}!</b></blockquote>

<blockquote>
✅ All words found!
🎉 Congratulations!
</blockquote>

<blockquote>
<b>Words were:</b> {', '.join(game['targets'])}
<b>👨‍💻 Dev:</b> Digan
</blockquote>
"""
            await update.message.reply_photo(
                photo=photo,
                caption=final_caption,
                parse_mode=ParseMode.HTML
            )
            await update.message.set_reaction("🎉")
            return
        
        # Update game state with progress
        new_list = []
        for w in game['targets']:
            if w in game['found']:
                new_list.append(f"✅ <s>{w}</s>")
            else:
                new_list.append(f"▫️ <code>{game['hints'][w]}</code>")
        
        progress = len(game['found'])
        total = len(game['targets'])
        
        caption = f"""
<blockquote><b>🧩 {to_fancy("WORD GRID CHALLENGE")}</b></blockquote>

<blockquote>
{"\n".join(new_list)}
</blockquote>

<blockquote>
<b>👇 Type the FULL word to solve!</b>
<b>👨‍💻 Dev:</b> Digan
<b>🎯 Found: {progress}/{total} words</b>
</blockquote>
"""     
        try:
            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=game['msg_id'],
                media=telegram.InputMediaPhoto(media=photo)
            )
            await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=game['msg_id'],
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏳️ Give Up", callback_data="giveup_wordgrid")]])
            )
            await update.message.set_reaction("✅")
        except Exception as e:
            print(f"Error updating game: {e}")
            # Try to send new message if edit fails
            try:
                msg = await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏳️ Give Up", callback_data="giveup_wordgrid")]]),
                    parse_mode=ParseMode.HTML
                )
                active_games[chat_id]['msg_id'] = msg.message_id
            except:
                pass

# --- 5. GIVE UP ---
async def give_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    if chat_id in active_games:
        game = active_games[chat_id]
        targets = game['targets']
        
        # Unpin the message
        if game.get('message_pinned'):
            try:
                await context.bot.unpin_chat_message(chat_id=chat_id, message_id=game['msg_id'])
            except:
                pass
        
        del active_games[chat_id]
        
        await query.message.edit_caption(
            caption=f"""
<blockquote><b>❌ {to_fancy("GAME OVER")}</b></blockquote>

<blockquote>
🏳️ You gave up!
</blockquote>

<blockquote>
<b>Words were:</b> {', '.join(targets)}
</blockquote>
""",
            parse_mode=ParseMode.HTML
        )
    else:
        await query.answer("No active game.", show_alert=True)

# --- 6. CALLBACK HANDLER (for give up) ---
async def grid_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function handles any grid-related callbacks
    query = update.callback_query
    data = query.data
    
    if data == "giveup_wordgrid":
        await give_up(update, context)

# Export functions for main.py
__all__ = [
    'start_wordgrid',
    'handle_word_guess',
    'grid_callback',
    'give_up'
]