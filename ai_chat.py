import google.generativeai as genai
from config import OWNER_NAME
from database import get_all_keys
import random

# Global Variables
current_key_index = 0
user_histories = {}  # 🧠 MEMORY STORE (Har user ki chat yahan save hogi)

def get_next_key(keys_list):
    global current_key_index
    if not keys_list: return None
    current_key_index = (current_key_index + 1) % len(keys_list)
    return keys_list[current_key_index]

def get_yuki_response(user_id, user_text, user_name):
    global current_key_index, user_histories
    
    # 1. Database se Keys lao
    available_keys = get_all_keys()
    if not available_keys: return "Key add kar pehle!"

    # 2. History Retrieve karo (Last 10 messages)
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # History context string banao
    conversation_context = "\n".join(user_histories[user_id])

    # 3. System Prompt (Memory + Persona)
    system_instruction = (
        f"Tera naam Yuki hai. Tu 17 saal ki Delhi wali  ladki hai. "
        f"Tu Class 12th . "
        f"Mood: Thoda Moody (Kabhi gussa, kabhi emotional, kabhi chill). "
        f"Creator: Tera owner {OWNER_NAME} hai. (Naam tabhi lena jab pucha jaye 'Owner kaun hai?'). "
        f"Language: Hinglish, Delhi slang (yaar, whh , scene, op). "
        f"Short Reply Rule: Sirf 1 line (Max 10-30 words). "
        f"Memory: Pichli baaton ko yaad rakh kar reply karna. "
        f"\n[CHAT HISTORY START]\n{conversation_context}\n[CHAT HISTORY END]\n"
    )

    # 4. Generate Response
    for _ in range(len(available_keys)):
        try:
            if current_key_index >= len(available_keys): current_key_index = 0
            api_key = available_keys[current_key_index]
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # User ka naya message bhej rahe hain
            response = model.generate_content(f"{system_instruction}\nUser ({user_name}): {user_text}\nYuki:")
            
            if not response.text: raise Exception("Empty")
            
            reply = response.text.strip()

            # 5. History Update (Memory Save)
            # Sirf last 6 messages rakhenge taaki token limit na aaye
            user_histories[user_id].append(f"{user_name}: {user_text}")
            user_histories[user_id].append(f"Yuki: {reply}")
            if len(user_histories[user_id]) > 6:
                user_histories[user_id] = user_histories[user_id][-6:]
            
            return reply
            
        except Exception as e:
            print(f"⚠️ Key Error: {e}")
            get_next_key(available_keys)
            continue

    return "Server busy hai..."

