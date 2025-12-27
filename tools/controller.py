import asyncio
from tools.youtube import YouTubeAPI
from tools.stream import play_stream, worker 
from tools.thumbnails import get_thumb
from tools.database import get_db_queue
from tools.queue import clear_queue
# 🔥 IMP: Humne jo async downloader banaya tha, usse import karo
from tools.downloader import download 

# Initialize YouTube
YouTube = YouTubeAPI()

async def process_stream(chat_id, user_name, query):
    """
    Flow: Search -> Status Check -> Thumbnail -> Async Download -> Stream
    """
    
    # --- 1. SEARCHING ---
    try:
        if "youtube.com" in query or "youtu.be" in query:
             # Link Handling
             if "v=" in query:
                 vidid = query.split("v=")[-1].split("&")[0]
             else:
                 vidid = query.split("/")[-1]
             
             # Details fetch karo (Fast)
             try:
                 title = await YouTube.title(query)
                 duration = await YouTube.duration(query)
                 thumbnail = await YouTube.thumbnail(query)
                 link = query
             except:
                 # Fallback logic if direct fetch fails
                 res, vidid = await YouTube.track(query)
                 title = res["title"]
                 duration = res["duration_min"]
                 thumbnail = res["thumb"]
                 link = res["link"]
        else:
            # Name Search
            result, vidid = await YouTube.track(query)
            if not result:
                return "❌ Song not found on YouTube.", None
            title = result["title"]
            duration = result["duration_min"]
            thumbnail = result["thumb"]
            link = result["link"]
            
    except Exception as e:
        return f"❌ Search Error: {e}", None

    # --- 🔥 2. GHOST QUEUE CLEANER (Fix for VC Off Bug) ---
    # Logic: Agar PyTgCalls actually connected nahi hai, lekin Database me queue hai,
    # toh purana queue saaf kar do taaki ye naya gaana 1st position par aaye.
    try:
        is_actually_connected = False
        try:
            # PyTgCalls V3 Compatible Check
            for call in worker.active_calls:
                if call.chat_id == chat_id:
                    is_actually_connected = True
                    break
        except: pass

        # Agar Bot VC me nahi hai, toh Queue Clear karo
        if not is_actually_connected:
            await clear_queue(chat_id)
            
    except Exception as e:
        print(f"VC Status Check Error: {e}")

    # --- 3. THUMBNAIL ---
    final_thumb = await get_thumb(vidid)
    if not final_thumb:
        final_thumb = thumbnail 

    # --- 4. ASYNC DOWNLOADING (Anti-Freeze) ---
    # 🔥 Humara naya downloader use kar rahe hain
    try:
        file_path = await download(link)
        if not file_path:
            return "❌ Download Failed (File not found)", None
    except Exception as e:
        return f"❌ Download Error: {e}", None

    # --- 5. PLAYING / QUEUING ---
    # play_stream ab khud decide karega ki Join karna hai ya Queue
    status, position = await play_stream(
        chat_id, 
        file_path, 
        title, 
        duration, 
        user_name, 
        link,        
        final_thumb  
    )

    # --- 6. RESULT RETURN ---
    response = {
        "title": title,
        "duration": duration,
        "thumbnail": final_thumb, 
        "user": user_name,
        "link": link,
        "vidid": vidid,
        "status": status,    # True = Now Playing, False = Queued
        "position": position 
    }
    
    return None, response
                 
