import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import json
import random

# Imports
from config import TELEGRAM_TOKEN
# 🔥 Note: get_game_keys use kar rahe hain (Chat wali key nahi)
from database import get_game_keys, update_wordseek_score, get_wordseek_leaderboard

# GAME STATE
active_games = {}

# --- GEMINI HELPER ---
def get_word_from_gemini():
    """Gemini se 1 Target Word lata hai using GAME KEYS"""
    keys = get_game_keys() # 🔥 Only Game Keys
    if not keys: return None

    prompt = (
        "Generate 1 random common English word (5 to 6 letters long). "
        "Provide the word, its phonetic transcription, and a clear hint (definition). "
        "Output strictly in JSON format: "
        '{"word": "VIDEO", "phonetic": "/ˈvɪd.i.əʊ/", "meaning": "To record using a video camera."}'
    )

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text: text = text.replace("```json", "").replace("```", "")
            data = json.loads(text)
            return data
        except: continue
    return None

# --- HELPER: GENERATE GRID ---
def generate_grid_string(target, guesses):
    target = target.upper()
    grid_msg = ""

    for guess in guesses:
        guess = guess.upper()
        row_emoji = ""
        for i, char in enumerate(guess):
            if char == target[i]:
                row_emoji += "🟩"
            elif char in target:
                row_emoji += "🟨"
            else:
                row_emoji += "🟥"
        grid_msg += f"{row_emoji} **{guess}**\n"
    return grid_msg

# --- COMMANDS ---

async def start_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id in active_games:
        await update.message.reply_text("⚠️ Game pehle se chal raha hai! `/end` karo ya guess karo.")
        return

    msg = await update.message.reply_text("🔄 **Loading Word Challenge...** 🧠")
    
    word_data = get_word_from_gemini()
    if not word_data:
        await msg.edit_text("❌ No Game API Keys found! Ask Admin to add keys.")
        return

    active_games[chat_id] = {
        "target": word_data['word'].upper(),
        "data": word_data,
        "guesses": [],
        "message_id": msg.message_id
    }
    
    length = len(word_data['word'])
    hint = word_data['meaning']

    # 🔥 BLOCK QUOTE ADDED HERE (>)
    text = (
        f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
        f"🔡 Word Length: **{length} Letters**\n"
        f"👇 *Guess the word below!*\n\n"
        f"> 💡 **Hint:** {hint}"
    )
    
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)

async def stop_wordseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in active_games:
        del active_games[chat_id]
        await update.message.reply_text("🛑 **Game Ended!**")
    else:
        await update.message.reply_text("❌ Koi game nahi chal raha.")

# --- GUESS HANDLER ---
async def handle_word_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.id not in active_games: return
    
    game = active_games[chat.id]
    target = game['target']
    user_guess = update.message.text.strip().upper()
    
    if len(user_guess) != len(target): return

    if user_guess in game['guesses']:
        await update.message.reply_text("Someone has already guessed your word. Please try another one!", quote=True)
        return

    game['guesses'].append(user_guess)
    
    # WIN SCENARIO
    if user_guess == target:
        user = update.effective_user
        points = 9
        update_wordseek_score(user.id, user.first_name, points, str(chat.id))
        
        data = game['data']
        del active_games[chat.id]
        
        await update.message.reply_text(
            f"🚬 ~ ` {user.first_name} ` ~ 🍷\n"
            f"{user_guess.title()}\n\n"
            f"Congrats! You guessed it correctly.\n"
            f"Added {points} to the leaderboard.\n"
            f"Start with /new\n\n"
            f"> **Correct Word:** {data['word']}\n"
            f"> **{data['word']}** {data.get('phonetic', '')}\n"
            f"> **Meaning:** {data['meaning']}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # WRONG GUESS - UPDATE GRID
        try:
            grid_text = generate_grid_string(target, game['guesses'])
            hint = game['data']['meaning']
            
            # 🔥 BLOCK QUOTE ADDED HERE ALSO (>)
            new_text = (
                f"🔥 **WORD GRID CHALLENGE** 🔥\n\n"
                f"{grid_text}\n"
                f"> 💡 **Hint:** {hint}"
            )
            
            await context.bot.edit_message_text(
                chat_id=chat.id,
                message_id=game['message_id'],
                text=new_text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception: pass

# --- LEADERBOARD ---
async def wordseek_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🌍 Global Top", callback_data="wrank_global"), InlineKeyboardButton("👥 Group Top", callback_data="wrank_group")]]
    await update.message.reply_text("🏆 **WordSeek Leaderboard**\nSelect Category 👇", reply_markup=InlineKeyboardMarkup(kb))

async def wordseek_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    
    if data.startswith("wrank_"):
        mode = data.split("_")[1]
        group_id = str(update.effective_chat.id) if mode == "group" else None
        
        leaderboard = get_wordseek_leaderboard(group_id)
        title = "🌍 Global" if mode == "global" else "👥 Group"
        msg = f"🏆 **{title} Leaderboard** 🏆\n\n"
        
        if not leaderboard: msg += "❌ No Data Found!"
        else:
            for i, p in enumerate(leaderboard, 1):
                score = p.get('global_score', 0) if mode == "global" else p.get('group_scores', {}).get(group_id, 0)
                msg += f"{i}. {p['name']} - 💎 {score}\n"
        
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="close_wrank")]]
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    if data == "close_wrank": await q.message.delete()
