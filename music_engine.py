import os
import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioQuality, VideoQuality  # Changed import
from config import API_ID, API_HASH, SESSION_STRING

# 1. Initialize Assistant Client
app = Client(
    "music_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# 2. Initialize Music Player
call_py = PyTgCalls(app)

# 🔥 START FUNCTION (Main.py me call hoga)
async def start_music_bot():
    print("🎵 Starting Music Assistant...")
    await app.start()
    await call_py.start()
    print("✅ Music System Ready!")

# 🔥 PLAY FUNCTION - Updated for py-tgcalls
async def play_audio(chat_id, file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        # Join the voice chat and play audio
        await call_py.join_group_call(
            chat_id,
            AudioPiped(
                file_path,
                audio_quality=AudioQuality.STUDIO
            )
        )
        print(f"✅ Now playing: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Play Error: {e}")
        return False

# 🔥 STOP FUNCTION - Updated API
async def stop_audio(chat_id):
    try:
        await call_py.leave_group_call(chat_id)
        print(f"✅ Stopped playback in chat: {chat_id}")
    except Exception as e:
        print(f"❌ Stop Error: {e}")

# 🔥 PAUSE/RESUME Functions (Optional additions)
async def pause_audio(chat_id):
    try:
        await call_py.pause_stream(chat_id)
        print(f"⏸️ Paused in chat: {chat_id}")
    except Exception as e:
        print(f"❌ Pause Error: {e}")

async def resume_audio(chat_id):
    try:
        await call_py.resume_stream(chat_id)
        print(f"▶️ Resumed in chat: {chat_id}")
    except Exception as e:
        print(f"❌ Resume Error: {e}")

# 🔥 SKIP/CHANGE TRACK Function
async def change_track(chat_id, new_file_path):
    try:
        if not os.path.exists(new_file_path):
            print(f"❌ File not found: {new_file_path}")
            return False
        
        await call_py.change_stream(
            chat_id,
            AudioPiped(
                new_file_path,
                audio_quality=AudioQuality.STUDIO
            )
        )
        print(f"🔀 Changed to: {new_file_path}")
        return True
    except Exception as e:
        print(f"❌ Change track Error: {e}")
        return False