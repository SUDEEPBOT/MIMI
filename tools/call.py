import asyncio
import os
from pyrogram import Client
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

from config import API_ID, API_HASH, SESSION, BOT_NAME
from tools.queue import pop_queue, clear_queue
from tools.database import remove_active_chat, is_active_chat, add_active_chat

class Call(PyTgCalls):
    def __init__(self):
        # Client Setup
        self.userbot = Client(
            name="MusicAssistant",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION,
        )
        # PyTgCalls Setup (Latest Version Style)
        super().__init__(self.userbot)

    async def start(self):
        print("🔵 Starting PyTgCalls Client...")
        await self.userbot.start()
        await super().start()
        print("✅ PyTgCalls Started!")

    async def join_call(self, chat_id, file_path, video=False):
        try:
            if video:
                stream = AudioVideoPiped(
                    file_path,
                    audio_parameters=HighQualityAudio(),
                    video_parameters=MediumQualityVideo(),
                )
            else:
                stream = AudioPiped(
                    file_path,
                    audio_parameters=HighQualityAudio(),
                )

            await self.join_group_call(
                int(chat_id),
                stream,
                stream_type=StreamType().pulse_stream,
            )
            await add_active_chat(chat_id)
        except Exception as e:
            print(f"❌ Join Error: {e}")
            raise e

    async def change_stream(self, chat_id, file_path, video=False):
        try:
            if video:
                stream = AudioVideoPiped(
                    file_path,
                    audio_parameters=HighQualityAudio(),
                    video_parameters=MediumQualityVideo(),
                )
            else:
                stream = AudioPiped(
                    file_path,
                    audio_parameters=HighQualityAudio(),
                )
                
            await self.change_stream(
                int(chat_id),
                stream,
            )
        except Exception as e:
            print(f"❌ Change Stream Error: {e}")
            raise e

    async def stop_stream(self, chat_id):
        try:
            await self.leave_group_call(int(chat_id))
            await remove_active_chat(chat_id)
            await clear_queue(chat_id)
        except Exception as e:
            pass

    async def pause_stream(self, chat_id):
        try:
            await self.pause_stream(int(chat_id))
        except:
            pass

    async def resume_stream(self, chat_id):
        try:
            await self.resume_stream(int(chat_id))
        except:
            pass

# Instance Create
MUSIC_CALL = Call()

# --- STREAM END HANDLER ---
@MUSIC_CALL.on_stream_end()
async def stream_end_handler(client, update: Update):
    if not isinstance(update, StreamAudioEnded):
        return
        
    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    # Queue Check
    next_song = await pop_queue(chat_id)

    if next_song:
        file = next_song["file"]
        try:
            await MUSIC_CALL.change_stream(chat_id, file)
        except Exception as e:
            await MUSIC_CALL.stop_stream(chat_id)
    else:
        await MUSIC_CALL.stop_stream(chat_id)
  
