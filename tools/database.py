import pymongo
from config import MONGO_DB_URI

# --- CONNECTION CHECK ---
if not MONGO_DB_URI:
    print("❌ ERROR: MONGO_DB_URI config.py mein nahi mila!")
    exit()

# Connect to MongoDB
try:
    client = pymongo.MongoClient(MONGO_DB_URI)
    db = client["MusicBot_Tools"] # Alag database name taaki mix na ho
    print("✅ Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")
    exit()

# --- COLLECTIONS ---
# Hum sirf 3 collections use karenge taaki database fast rahe
active_db = db.active_chats    # Kahan Audio chal raha hai
video_db = db.video_chats      # Kahan Video chal raha hai
queue_db = db.queues           # Queue data

# --- ACTIVE CHAT FUNCTIONS ---
# Ye check karta hai ki kis group mein VC join hai

def is_active_chat(chat_id: int):
    """Check agar Audio Play ho raha hai"""
    data = active_db.find_one({"chat_id": chat_id})
    return True if data else False

def add_active_chat(chat_id: int):
    """Group ko Audio Active list mein daalo"""
    if not is_active_chat(chat_id):
        active_db.insert_one({"chat_id": chat_id})

def remove_active_chat(chat_id: int):
    """Group ko Audio Active list se hatao"""
    active_db.delete_one({"chat_id": chat_id})

# --- VIDEO CHAT FUNCTIONS ---
# Ye check karta hai ki kis group mein Video chal raha hai

def is_active_video_chat(chat_id: int):
    """Check agar Video Play ho raha hai"""
    data = video_db.find_one({"chat_id": chat_id})
    return True if data else False

def add_active_video_chat(chat_id: int):
    """Group ko Video Active list mein daalo"""
    if not is_active_video_chat(chat_id):
        video_db.insert_one({"chat_id": chat_id})

def remove_active_video_chat(chat_id: int):
    """Group ko Video Active list se hatao"""
    video_db.delete_one({"chat_id": chat_id})

# --- QUEUE FUNCTIONS ---
# Ye sabse zaroori hai: Queue ko Database mein save karna

def get_db_queue(chat_id: int):
    """
    Database se Queue list nikalta hai.
    Returns: List []
    """
    data = queue_db.find_one({"chat_id": chat_id})
    if data:
        return data.get("queue", [])
    return []

def save_db_queue(chat_id: int, queue_list: list):
    """
    Queue list ko Database mein save karta hai.
    Upsert=True ka matlab: Agar nahi hai to banao, hai to update karo.
    """
    queue_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"queue": queue_list}},
        upsert=True
    )

def clear_db_queue(chat_id: int):
    """Queue ko delete kar deta hai"""
    queue_db.delete_one({"chat_id": chat_id})

# --- CLEANUP ON RESTART ---
# Jab bot restart ho, to purane "Active" chats ko hata dena chahiye
# warna bot confuse ho jayega.

def clean_restart_data():
    try:
        active_db.delete_many({})
        video_db.delete_many({})
        print("🧹 Active Chat Data Cleared for Fresh Start.")
    except Exception as e:
        print(f"⚠️ Cleanup Error: {e}")

# Jaise hi ye file load hogi, purana data saaf ho jayega
clean_restart_data()
