import asyncio
import os
import html 
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, Update
from pytgcalls.types import HighQualityAudio 
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode

# Configs
from config import API_ID, API_HASH, SESSION, BOT_TOKEN, OWNER_NAME, LOG_GROUP_ID, INSTAGRAM_LINK
# 🔥 Important: pop_queue ab next song return karega
from tools.queue import put_queue, pop_queue, clear_queue, get_queue
from tools.database import is_active_chat, add_active_chat, remove_active_chat

# --- GLOBAL DICTIONARIES ---
LAST_MSG_ID = {}   
QUEUE_MSG_ID = {}  

# --- CLIENT SETUP ---
from pyrogram import Client
worker_app = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)
worker = PyTgCalls(worker_app)

main_bot = Bot(token=BOT_TOKEN)

# --- HELPER: PROGRESS BAR ---
def get_progress_bar(duration):
    try:
        bar = "◉—————————" 
        return f"{bar}"
    except:
        return "◉—————————"

# --- 🔥 STARTUP LOGIC ---
async def start_music_worker():
    print("🔵 Starting Music Assistant (VIP Style)...")
    try:
        await worker_app.start()
        await worker.start()
        print("✅ Assistant & PyTgCalls Started!")
        if LOG_GROUP_ID:
            try:
                await worker_app.send_message(int(LOG_GROUP_ID), "✅ Music System Online!")
            except: pass
    except Exception as e:
        print(f"❌ Assistant Error: {e}")

# --- 1. PLAY LOGIC (Trust No One) ---
async def play_stream(chat_id, file_path, title, duration, user, link, thumbnail):
    safe_title = html.escape(title)
    safe_user = html.escape(user)

    stream = AudioPiped(file_path, audio_parameters=HighQualityAudio())

    # 🔥 Direct Join Strategy
    try:
        # Pehle try karo join karne ka
        await worker.join_group_call(int(chat_id), stream)
        
        # Success!
        await add_active_chat(chat_id)
        await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
        return True, 0

    except Exception as e:
        err_str = str(e).lower()
        
        # Case 1: Already Joined (VC Bug Fix)
        if "already" in err_str or "participant" in err_str:
            # Check karo kya sach me active hai?
            is_active = False
            try:
                for call in worker.active_calls:
                    if call.chat_id == chat_id:
                        is_active = True
                        break
            except: pass

            if is_active:
                # Sach me joined hai -> Queue me daalo
                position = await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
                return False, position
            else:
                # Ghost Connection -> Leave & Rejoin
                try:
                    await worker.leave_group_call(int(chat_id))
                    await asyncio.sleep(0.5)
                    await worker.join_group_call(int(chat_id), stream)
                    await add_active_chat(chat_id)
                    await put_queue(chat_id, file_path, safe_title, duration, safe_user, link, thumbnail)
                    return True, 0
                except Exception as final_e:
                    return None, str(final_e)

        # Case 2: VC Off hai
        elif "no active group call" in err_str:
            return None, "❌ **Voice Chat is OFF!**\nPlease start Video Chat first."
        
        else:
            print(f"❌ Play Error: {e}")
            return None, str(e)

# --- 2. AUTO PLAY HANDLER (Fixed Logic) ---
@worker.on_stream_end()
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass 
    
    # 🔥 CRITICAL FIX: pop_queue se seedha Next Song mango
    # (Ye current ko delete karega aur next return karega)
    next_song = await pop_queue(chat_id)

    if next_song:
        # Data Extract
        file = next_song["file"]
        title = next_song["title"] 
        duration = next_song["duration"]
        user = next_song["by"] 
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        
        try:
            stream = AudioPiped(file, audio_parameters=HighQualityAudio())
            
            # Try switching stream
            try:
                await worker.change_stream(chat_id, stream)
            except:
                # Fail hua to Re-Join (Anti-Freeze)
                await worker.join_group_call(chat_id, stream)
            
            # UI Message
            if len(title) > 30: d_title = title[:30] + "..."
            else: d_title = title
            
            bar_display = get_progress_bar(duration)

            buttons = [
                [InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")],
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [
                    InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link),
                    InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)
                ],
                [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
            ]
            
            caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{d_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
            msg = await main_bot.send_photo(
                chat_id,
                photo=thumbnail,
                caption=caption,
                has_spoiler=True, 
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
            LAST_MSG_ID[chat_id] = msg.message_id

        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await stop_stream(chat_id)

    else:
        # Queue Empty -> Bye Bye
        print(f"✅ Queue Empty for {chat_id}, Leaving.")
        await stop_stream(chat_id)

# --- 3. SKIP LOGIC ---
async def skip_stream(chat_id):
    # Old msg delete
    if chat_id in LAST_MSG_ID:
        try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
        except: pass

    # Next Song fetch
    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        title = next_song["title"]
        link = next_song["link"]
        thumbnail = next_song["thumbnail"]
        duration = next_song["duration"]
        user = next_song["by"]

        try:
            stream = AudioPiped(file, audio_parameters=HighQualityAudio())
            await worker.change_stream(chat_id, stream)
            
            # UI Code (Same as above)
            if len(title) > 30: d_title = title[:30] + "..."
            else: d_title = title
            bar_display = get_progress_bar(duration)
            buttons = [
                [InlineKeyboardButton(f"00:00 {bar_display} {duration}", callback_data="GetTimer")],
                [
                    InlineKeyboardButton("II", callback_data="music_pause"),
                    InlineKeyboardButton("▶", callback_data="music_resume"),
                    InlineKeyboardButton("‣‣I", callback_data="music_skip"),
                    InlineKeyboardButton("▢", callback_data="music_stop")
                ],
                [InlineKeyboardButton("📺 ʏᴏᴜᴛᴜʙᴇ", url=link), InlineKeyboardButton("📸 ɪɴsᴛᴀɢʀᴀᴍ", url=INSTAGRAM_LINK)],
                [InlineKeyboardButton("🗑 ᴄʟᴏsᴇ ᴘʟᴀʏᴇʀ", callback_data="force_close")]
            ]
            caption = f"""
<b>✅ sᴛᴀʀᴛᴇᴅ sᴛʀᴇᴀᴍɪɴɢ</b>

<blockquote><b>🎸 ᴛɪᴛʟᴇ :</b> <a href="{link}">{d_title}</a>
<b>⏳ ᴅᴜʀᴀᴛɪᴏɴ :</b> <code>{duration}</code>
<b>👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {user}</blockquote>

{bar_display}

<blockquote><b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ :</b> {OWNER_NAME}</blockquote>
"""
            msg = await main_bot.send_photo(chat_id, photo=thumbnail, caption=caption, has_spoiler=True, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
            LAST_MSG_ID[chat_id] = msg.message_id
            return True 
        except: return False
    else:
        await stop_stream(chat_id)
        return False

# --- 4. STOP & CONTROL LOGIC ---
async def stop_stream(chat_id):
    try:
        await worker.leave_group_call(int(chat_id))
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)
        if chat_id in LAST_MSG_ID:
            try: await main_bot.delete_message(chat_id, LAST_MSG_ID[chat_id])
            except: pass
        return True
    except: return False

async def pause_stream(chat_id):
    try:
        await worker.pause_stream(chat_id)
        return True
    except: return False

async def resume_stream(chat_id):
    try:
        await worker.resume_stream(chat_id)
        return True
    except: return False
    
