import time

# --- CONFIGURATION (Bhot Strict Settings) ---
MAX_MESSAGES = 5       # Sirf 5 Message allow hain...
TIME_WINDOW = 6        # ...6 Second ke andar.
BLOCK_DURATION = 300   # 5 Minute ka Block.

# --- MEMORY ---
user_timestamps = {}   # {user_id: [time1, time2, time3...]}
blocked_users = {}     # {user_id: unlock_time}

def check_spam(user_id):
    current_time = time.time()
    
    # 1. Check agar banda pehle se Blocked hai
    if user_id in blocked_users:
        if current_time < blocked_users[user_id]:
            return "BLOCKED"  # Saza abhi baki hai
        else:
            del blocked_users[user_id]  # Saza khatam -> Unblock

    # 2. Timestamp Record Karo
    if user_id not in user_timestamps:
        user_timestamps[user_id] = []
    
    # Naya message ka time list me daalo
    user_timestamps[user_id].append(current_time)

    # 3. Purane timestamps hatao (Jo window se bahar hain)
    # Filter: Sirf wahi time rakho jo (Current Time - Window) se naye hain
    user_timestamps[user_id] = [
        t for t in user_timestamps[user_id] 
        if current_time - t <= TIME_WINDOW
    ]

    # 4. Count Check Karo
    if len(user_timestamps[user_id]) > MAX_MESSAGES:
        # Limit Cross! Block him.
        blocked_users[user_id] = current_time + BLOCK_DURATION
        del user_timestamps[user_id] # Data clear karo
        print(f"🚫 BLOCKED USER: {user_id} for Spamming!")
        return "NEW_BLOCK"

    return "OK"
