import pymongo
from config import MONGO_DB_URI

# --- CONNECTION CHECK ---
if not MONGO_DB_URI:
    print("❌ ERROR: MONGO_DB_URI config.py mein nahi mila!")
    exit()

# Connect to MongoDB
try:
    client = pymongo.MongoClient(MONGO_DB_URI)
    db = client["MusicBot_Tools"]
    print("✅ Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
    exit()

# --- COLLECTIONS ---
active_db = db.active_chats
video_db = db.video_chats
queue_db = db.queues

# --- ACTIVE CHAT FUNCTIONS (Async for stream.py) ---

# ✅ Ye function missing tha, maine add kar diya
def get_active_chats():
    """Start hone par active chats ki list deta hai"""
    chats = active_db.find({})
    return [x["chat_id"] for x in chats]

async def is_active_chat(chat_id: int):
    """Check agar Audio Play ho raha hai"""
    data = active_db.find_one({"chat_id": chat_id})
    return True if data else False

async def add_active_chat(chat_id: int):
    """Group ko Audio Active list mein daalo"""
    # Note: internal call mein await lagaya
    check = await is_active_chat(chat_id)
    if not check:
        active_db.insert_one({"chat_id": chat_id})

async def remove_active_chat(chat_id: int):
    """Group ko Audio Active list se hatao"""
    active_db.delete_one({"chat_id": chat_id})

# --- VIDEO CHAT FUNCTIONS ---

async def is_active_video_chat(chat_id: int):
    data = video_db.find_one({"chat_id": chat_id})
    return True if data else False

async def add_active_video_chat(chat_id: int):
    check = await is_active_video_chat(chat_id)
    if not check:
        video_db.insert_one({"chat_id": chat_id})

async def remove_active_video_chat(chat_id: int):
    video_db.delete_one({"chat_id": chat_id})

# --- QUEUE FUNCTIONS ---

async def get_db_queue(chat_id: int):
    data = queue_db.find_one({"chat_id": chat_id})
    if data:
        return data.get("queue", [])
    return []

async def save_db_queue(chat_id: int, queue_list: list):
    queue_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"queue": queue_list}},
        upsert=True
    )

async def clear_db_queue(chat_id: int):
    queue_db.delete_one({"chat_id": chat_id})

# --- CLEANUP ON RESTART ---
def clean_restart_data():
    try:
        active_db.delete_many({})
        video_db.delete_many({})
        print("🧹 Active Chat Data Cleared for Fresh Start.")
    except Exception as e:
        print(f"⚠️ Cleanup Error: {e}")

# Run Cleanup
clean_restart_data()

