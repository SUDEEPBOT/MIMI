import pymongo
from config import MONGO_URL

# --- DATABASE CONNECTION ---
try:
    client = pymongo.MongoClient(MONGO_URL)
    db = client["CasinoBot"]
    
    # Collections
    users_col = db["users"]
    groups_col = db["groups"]
    investments_col = db["investments"]
    codes_col = db["codes"]
    keys_col = db["api_keys"]  # <-- NEW: API Keys yahan save hongi
    
    print("✅ Database Connected!")
except Exception as e:
    print(f"❌ DB Error: {e}")

# --- USER FUNCTIONS ---

def check_registered(user_id):
    """Check if user exists"""
    return users_col.find_one({"_id": user_id}) is not None

def register_user(user_id, name):
    """Register new user with Bonus"""
    if check_registered(user_id): return False
    user = {
        "_id": user_id, 
        "name": name, 
        "balance": 500,  # Bonus
        "loan": 0,
        "titles": []     # Shop items yahan aayenge
    } 
    users_col.insert_one(user)
    return True

def get_user(user_id):
    """Get full user object"""
    return users_col.find_one({"_id": user_id})

def update_balance(user_id, amount):
    """Add or subtract money"""
    users_col.update_one({"_id": user_id}, {"$inc": {"balance": amount}}, upsert=True)

def get_balance(user_id):
    """Get current balance"""
    user = users_col.find_one({"_id": user_id})
    return user["balance"] if user else 0

# --- GROUP & MARKET FUNCTIONS ---

def update_group_activity(group_id, group_name):
    """Increase group activity score"""
    groups_col.update_one(
        {"_id": group_id},
        {"$set": {"name": group_name}, "$inc": {"activity": 1}},
        upsert=True
    )

def get_group_price(group_id):
    """Calculate Share Price based on Activity"""
    grp = groups_col.find_one({"_id": group_id})
    if not grp: return 10.0
    # Formula: Base 10 + (Score * 0.5)
    return round(10 + (grp.get("activity", 0) * 0.5), 2)

# --- 🔥 NEW: API KEY MANAGEMENT FUNCTIONS ---

def add_api_key(api_key):
    """Admin se Key lekar DB me save karega"""
    if keys_col.find_one({"key": api_key}):
        return False # Already exists
    keys_col.insert_one({"key": api_key})
    return True

def remove_api_key(api_key):
    """Key delete karega"""
    result = keys_col.delete_one({"key": api_key})
    return result.deleted_count > 0

def get_all_keys():
    """Saari keys ki list return karega AI Chat ke liye"""
    keys = list(keys_col.find({}, {"_id": 0, "key": 1}))
    return [k["key"] for k in keys]
    
