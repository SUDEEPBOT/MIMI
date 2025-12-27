import os
from config import DURATION_LIMIT_MIN
from tools.database import get_db_queue, save_db_queue, clear_db_queue

QUEUE_LIMIT = 50

async def put_queue(chat_id, file, title, duration, user, link, thumbnail, stream_type="audio"):
    """
    Song ko queue mein add karta hai.
    """
    if not isinstance(file, str):
        print(f"❌ Queue Error: File path text nahi hai! ({type(file)})")
        return {"error": "File Error"}

    queue = await get_db_queue(chat_id)

    if len(queue) >= QUEUE_LIMIT:
        return {"error": "Queue Full"}

    song = {
        "title": title,
        "file": str(file),
        "duration": duration,
        "by": user,
        "link": link,
        "thumbnail": thumbnail,
        "streamtype": stream_type,
        "played": 0,
    }

    queue.append(song)
    await save_db_queue(chat_id, queue)

    # Position return karo
    return len(queue) - 1


async def pop_queue(chat_id):
    """
    Current song (Index 0) ko delete karta hai aur NEXT SONG return karta hai.
    """
    queue = await get_db_queue(chat_id)

    if not queue:
        return None

    # 1. Jo baj raha tha (Index 0) usse remove karo
    queue.pop(0)

    # 2. Database update karo
    await save_db_queue(chat_id, queue)

    # 3. Ab check karo kya koi aur gaana bacha hai?
    # Agar haan, toh wo ab Index 0 par aa gaya hoga. Wahi Next Song hai.
    if queue:
        next_song = queue[0]
        
        # Safety Check
        if "file" not in next_song:
            print("❌ Queue Corrupted: Next song data incomplete.")
            return None
            
        return next_song

    return None

async def get_queue(chat_id):
    """
    Puri list return karta hai.
    """
    return await get_db_queue(chat_id)

async def clear_queue(chat_id):
    """
    Database se queue saaf karta hai.
    """
    await clear_db_queue(chat_id)
    print(f"🧹 Queue Cleared Silently for {chat_id}")
    
