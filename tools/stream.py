from pyrogram import Client
from pytgcalls import PyTgCalls

# py-tgcalls 0.9.7 imports
from pytgcalls.types import InputAudioStream, InputStream
from pytgcalls.types.input_stream.quality import HighQualityAudio

from config import API_ID, API_HASH, SESSION, LOGGER_ID
from tools.queue import put_queue, pop_queue, clear_queue
from tools.database import (
    is_active_chat,
    add_active_chat,
    remove_active_chat,
)

# ─────────────────────────────────────
# CLIENT SETUP (Assistant / Userbot)
# ─────────────────────────────────────

worker = Client(
    "MusicWorker",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    in_memory=True,
)

call_py = PyTgCalls(worker)

# ─────────────────────────────────────
# START MUSIC WORKER
# ─────────────────────────────────────

async def start_music_worker():
    try:
        await worker.start()
        await call_py.start()

        print("✅ Music Assistant Started")

        try:
            await worker.send_message(
                LOGGER_ID,
                "✅ **Music Assistant Started Successfully** 🎵\n\n"
                "• Engine: PyTgCalls 0.9.7\n"
                "• Mode: Audio VC\n"
                "• Status: Ready 🚀"
            )
        except Exception as log_err:
            print(f"⚠️ Logger Error: {log_err}")

    except Exception as e:
        print(f"❌ Assistant Start Error: {e}")

# ─────────────────────────────────────
# PLAY STREAM
# ─────────────────────────────────────

async def play_stream(chat_id, file_path, title, duration, user):
    """
    - Agar VC active hai → Queue
    - Nahi hai → Direct Play
    """

    # 🔒 SAFETY: file_path must be STRING
    if not isinstance(file_path, str):
        print("❌ Invalid file path (not string):", file_path)
        return None, None

    # 1️⃣ Already playing → Queue
    if is_active_chat(chat_id):
        position = await put_queue(chat_id, file_path, title, duration, user)
        return False, position

    # 2️⃣ Not playing → Join VC & Play
    try:
        # FIXED: Wrapped in InputAudioStream
        stream = InputStream(
            InputAudioStream(
                file_path,
                parameters=HighQualityAudio()
            )
        )

        await call_py.join_group_call(
            int(chat_id),
            stream,
        )

        add_active_chat(chat_id)
        await put_queue(chat_id, file_path, title, duration, user)
        return True, 0

    except Exception as e:
        print(f"❌ Play Error: {e}")
        return None, None

# ─────────────────────────────────────
# AUTO PLAY (ON STREAM END)
# ─────────────────────────────────────

@call_py.on_stream_end()
async def stream_end_handler(_, update):
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    # Current song hatao, next lo
    next_song = await pop_queue(chat_id)

    if next_song:
        file_path = next_song.get("file")

        # 🔒 SAFETY CHECK
        if not isinstance(file_path, str):
            print("❌ Queue Corrupted: file is not string")
            await call_py.leave_group_call(chat_id)
            remove_active_chat(chat_id)
            await clear_queue(chat_id)
            return

        try:
            # FIXED: Wrapped in InputAudioStream
            stream = InputStream(
                InputAudioStream(
                    file_path,
                    parameters=HighQualityAudio()
                )
            )

            await call_py.change_stream(
                chat_id,
                stream,
            )
        except Exception as e:
            print(f"❌ Auto-Play Error: {e}")
            await call_py.leave_group_call(chat_id)
            remove_active_chat(chat_id)
            await clear_queue(chat_id)

    else:
        # Queue khatam → Leave VC
        print("🛑 Queue Empty. Leaving VC.")
        try:
            await call_py.leave_group_call(chat_id)
        except:
            pass
        remove_active_chat(chat_id)
        await clear_queue(chat_id)

# ─────────────────────────────────────
# STOP STREAM
# ─────────────────────────────────────

async def stop_stream(chat_id):
    try:
        await call_py.leave_group_call(int(chat_id))
        remove_active_chat(chat_id)
        await clear_queue(chat_id)
        return True
    except Exception as e:
        print(f"❌ Stop Error: {e}")
        return False
        
