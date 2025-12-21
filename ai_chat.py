import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys, get_sticker_packs
import random
import pytz # Timezone ke liye
from datetime import datetime # Time calculation ke liye

# Global Variables
current_key_index = 0
user_histories = {} 

# --- TEXT GENERATION (Gemini AI) ---
def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    if not available_keys: 
        return "Mimi abhi so rahi hai... (No API Key) 😴"

    # 2. History Retrieve karo
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    conversation_context = "\n".join(user_histories[user_id])

    # 🔥 TIME & DATE CALCULATION (IST - India Time) 🔥
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    
    # Format: "Monday, 22 December 2025 | Time: 10:30 PM"
    date_time_str = now.strftime("%A, %d %B %Y | Time: %I:%M %p")
    
    # 3. 🔥 SYSTEM PROMPT (Mimi - Smart & Time Aware) 🔥
    full_prompt = (
        f"System: Tera naam Mimi hai. Tu 19 saal ki ek cute college student hai. "
        f"Tera Creator: {OWNER_NAME}. "
        f"Abhi ka Time aur Date hai: {date_time_str}. (Iske hisaab se wish karna jaise Good Morning/Night). "
        f"Personality: Tu bohot friendly, bubbly aur thodi naughty hai. "
        f"Language: Hinglish (Roman Hindi + English Mix). "
        f"Context: "
        f"1. Agar user time/date puche to upar wale time se batana. "
        f"2. Agar user voice note mangne ko kahe, to cute sa haan bolna. "
        f"Speaking Style: "
        f"1. Chhote replies de (Max 15 words). "
        f"2. Emojis ka use kar (😋, 😅, 😁, 🙈, ❤️). "
        f"3. Bilkul insaan ki tarah baat kar (jaise: 'hehe', 'aaj sunday hai na', 'itni raat ko jag rahe ho?'). "
        f"\n\nChat History:\n{conversation_context}\n\n"
        f"User ({user_name}): {user_text}\n"
        f"Mimi (Time: {date_time_str}):"
    )

    last_error = ""

    # 4. Try All Keys (Auto-Rotation)
    for _ in range(len(available_keys)):
        try:
            # Safe Index Access
            current_key_index = current_key_index % len(available_keys)
            api_key = available_keys[current_key_index]
            
            genai.configure(api_key=api_key)
            
            # 🔥 Model: Gemini 1.5 Flash
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate
            response = model.generate_content(full_prompt)
            
            if not response.text: 
                raise Exception("Empty Response")
            
            reply = response.text.strip()

            # Save History
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Mimi: {reply}")
            
            # Memory Limit
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]
            
            return reply
            
        except Exception as e:
            last_error = str(e)
            print(f"❌ Key {current_key_index} Failed: {e}")
            current_key_index += 1
            continue

    return f"Mimi abhi busy hai assignment mein! 📚\n(Server Error: {last_error})"

# --- 🔥 STICKER GENERATION ---
async def get_mimi_sticker(bot):
    try:
        packs = get_sticker_packs()
        if not packs: return None

        random_pack_name = random.choice(packs)
        try:
            sticker_set = await bot.get_sticker_set(random_pack_name)
        except:
            return None 
        
        if not sticker_set or not sticker_set.stickers:
            return None

        random_sticker = random.choice(sticker_set.stickers)
        return random_sticker.file_id

    except Exception as e:
        print(f"❌ Sticker Error: {e}")
        return None
