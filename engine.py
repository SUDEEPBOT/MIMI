import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from config import API_ID, API_HASH, STRING_SESSION

# Userbot Setup
userbot = Client(
    "MusicAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

call_py = PyTgCalls(userbot)

async def start_music_engine():
    print("🔵 Starting Userbot & PyTgCalls...")
    await userbot.start()
    await call_py.start()
    print("✅ Music Engine Ready!")

async def join_group(chat_id, invite_link):
    try:
        try:
            await userbot.get_chat_member(chat_id, "me")
            return True
        except:
            pass 
        
        if invite_link:
            await userbot.join_chat(invite_link)
            return True
    except Exception as e:
        print(f"Join Error: {e}")
        return False

async def play_audio(chat_id, file_path):
    try:
        await call_py.play(
            int(chat_id),
            MediaStream(
                file_path,
                video_flags=MediaStream.Flags.IGNORE 
            )
        )
        return True
    except Exception as e:
        print(f"Play Error: {e}")
        return False

async def play_video(chat_id, file_path):
    try:
        await call_py.play(
            int(chat_id),
            MediaStream(file_path)
        )
        return True
    except Exception as e:
        print(f"Video Play Error: {e}")
        return False

async def stop_stream(chat_id):
    try:
        await call_py.leave_call(int(chat_id))
        return True
    except:
        return False
        
