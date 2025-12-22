import time

# --- CONFIGURATION (Settings yahan badlo) ---
MAX_MESSAGES = 6       # 5 se zyada message...
TIME_WINDOW = 3        # ...agar 3 second ke andar aaye to SPAM hai.
BLOCK_DURATION = 300   # 300 Seconds = 5 Minutes Block

# --- STORAGE (Temporary Memory) ---
user_activity = {}
blocked_users = {}

def check_spam(user_id):
    current_time = time.time()
    
    # 1. Check karo banda pehle se Blocked hai kya?
    if user_id in blocked_users:
        unblock_time = blocked_users[user_id]
        if current_time < unblock_time:
            return "BLOCKED" # Abhi bhi saza kaat raha hai
        else:
            del blocked_users[user_id] # Saza khatam, Unblock

    # 2. User ka spam check karo
    if user_id not in user_activity:
        user_activity[user_id] = {'count': 1, 'timestamp': current_time}
    else:
        data = user_activity[user_id]
        
        # Agar Time Window ke andar hai
        if current_time - data['timestamp'] <= TIME_WINDOW:
            data['count'] += 1
            
            # Agar limit cross ho gayi (Spam Detected)
            if data['count'] > MAX_MESSAGES:
                blocked_users[user_id] = current_time + BLOCK_DURATION
                del user_activity[user_id] # Record clear karo
                return "NEW_BLOCK" # Abhi fresh block hua hai
        else:
            # Time window nikal gaya, reset karo (Normal user)
            user_activity[user_id] = {'count': 1, 'timestamp': current_time}

    return "OK"
