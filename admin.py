from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import (
    users_col, groups_col, codes_col, update_balance, 
    add_api_key, remove_api_key, get_all_keys,
    add_game_key, remove_game_key, get_game_keys,
    add_sticker_pack, remove_sticker_pack, get_sticker_packs,
    wipe_database, set_economy_status, get_economy_status,
    set_logger_group, delete_logger_group
)

# Global variable state maintain karne ke liye
ADMIN_INPUT_STATE = {} 

# --- 1. MAIN ADMIN PANEL ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(OWNER_ID): return

    # Clear old state
    if update.effective_user.id in ADMIN_INPUT_STATE:
        del ADMIN_INPUT_STATE[update.effective_user.id]
    
    eco_status = "🟢 ON" if get_economy_status() else "🔴 OFF"
    chat_keys = len(get_all_keys())
    game_keys = len(get_game_keys())
    stickers = len(get_sticker_packs())

    text = (
        f"👮‍♂️ **ADMIN CONTROL PANEL**\n\n"
        f"⚙️ **Economy:** {eco_status}\n"
        f"💬 **Chat Keys:** `{chat_keys}`\n"
        f"🎮 **Game Keys:** `{game_keys}`\n"
        f"👻 **Stickers:** `{stickers}`\n\n"
        f"👇 Select an action:"
    )

    kb = [
        [InlineKeyboardButton(f"Economy: {eco_status}", callback_data="admin_toggle_eco")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_cast_ask"), InlineKeyboardButton("🎁 Create Code", callback_data="admin_code_ask")],
        [InlineKeyboardButton("💰 Add Money", callback_data="admin_add_ask"), InlineKeyboardButton("💸 Take Money", callback_data="admin_take_ask")],
        
        # Keys Management
        [InlineKeyboardButton("🔑 Chat Keys", callback_data="admin_chat_keys_menu"), InlineKeyboardButton("🎮 Game Keys", callback_data="admin_game_keys_menu")],
        
        # Stickers & Logger
        [InlineKeyboardButton("👻 Stickers", callback_data="admin_stickers_menu"), InlineKeyboardButton("📝 Logger", callback_data="admin_logger_menu")],
        
        [InlineKeyboardButton("☢️ WIPE DATA", callback_data="admin_wipe_ask"), InlineKeyboardButton("❌ Close", callback_data="admin_close")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

# --- 2. CALLBACK HANDLER ---
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user_id = q.from_user.id
    
    if str(user_id) != str(OWNER_ID):
        await q.answer("❌ Sirf Owner ke liye hai!", show_alert=True)
        return

    # --- SUB-MENUS ---
    if data == "admin_chat_keys_menu":
        kb = [[InlineKeyboardButton("➕ Add Key", callback_data="admin_key_add")], [InlineKeyboardButton("➖ Del Key", callback_data="admin_key_del")], [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        await q.edit_message_text("🔑 **Chat API Keys (Gemini)**", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "admin_game_keys_menu":
        kb = [[InlineKeyboardButton("➕ Add Key", callback_data="admin_game_key_add")], [InlineKeyboardButton("➖ Del Key", callback_data="admin_game_key_del")], [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        await q.edit_message_text("🎮 **Game API Keys (WordSeek)**", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "admin_stickers_menu":
        kb = [[InlineKeyboardButton("➕ Add Pack", callback_data="admin_pack_add")], [InlineKeyboardButton("➖ Del Pack", callback_data="admin_pack_del")], [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        await q.edit_message_text("👻 **Sticker Packs Management**", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "admin_logger_menu":
        kb = [[InlineKeyboardButton("📝 Set Logger", callback_data="admin_set_logger")], [InlineKeyboardButton("🗑 Del Logger", callback_data="admin_del_logger")], [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        await q.edit_message_text("📝 **Logger Settings**", reply_markup=InlineKeyboardMarkup(kb))
        return

    # --- INPUT TRIGGERS (ADD & DELETE) ---
    
    # 1. Chat Keys
    if data == "admin_key_add":
        ADMIN_INPUT_STATE[user_id] = 'add_key'
        await q.edit_message_text("➕ Send Gemini API Key:")
    elif data == "admin_key_del":
        ADMIN_INPUT_STATE[user_id] = 'del_key'
        keys = "\n".join([f"`{k}`" for k in get_all_keys()])
        await q.edit_message_text(f"➖ Send Chat Key to delete:\n\n{keys}", parse_mode=ParseMode.MARKDOWN)

    # 2. Game Keys
    elif data == "admin_game_key_add":
        ADMIN_INPUT_STATE[user_id] = 'add_game_key'
        await q.edit_message_text("🎮 Send WordSeek API Key:")
    elif data == "admin_game_key_del":
        ADMIN_INPUT_STATE[user_id] = 'del_game_key'
        keys = "\n".join([f"`{k}`" for k in get_game_keys()])
        await q.edit_message_text(f"➖ Send Game Key to delete:\n\n{keys}", parse_mode=ParseMode.MARKDOWN)

    # 3. Stickers
    elif data == "admin_pack_add":
        ADMIN_INPUT_STATE[user_id] = 'add_pack'
        await q.edit_message_text("👻 Send Sticker Pack Name or Link:")
    elif data == "admin_pack_del":
        ADMIN_INPUT_STATE[user_id] = 'del_pack'
        packs = "\n".join([f"`{p}`" for p in get_sticker_packs()])
        await q.edit_message_text(f"➖ Send Pack Name to delete:\n\n{packs}", parse_mode=ParseMode.MARKDOWN)

    # 4. Others
    elif data == "admin_cast_ask":
        ADMIN_INPUT_STATE[user_id] = 'broadcast'
        await q.edit_message_text("📢 Send anything to Broadcast (Text/Photo/Video):")
    elif data == "admin_add_ask":
        ADMIN_INPUT_STATE[user_id] = 'add_money'
        await q.edit_message_text("💰 Format: `UserID Amount` (Ex: `123 5000`)")
    elif data == "admin_take_ask":
        ADMIN_INPUT_STATE[user_id] = 'take_money'
        await q.edit_message_text("💸 Format: `UserID Amount` (Ex: `123 5000`)")
    elif data == "admin_set_logger":
        ADMIN_INPUT_STATE[user_id] = "waiting_logger_id"
        await q.edit_message_text("📝 Send Logger Group ID:")
    elif data == "admin_code_ask":
        ADMIN_INPUT_STATE[user_id] = 'create_code'
        await q.edit_message_text("🎁 Format: `Name Amount Limit` (Ex: `MIMI100 500 10`)")

    # --- ACTIONS ---
    elif data == "admin_toggle_eco":
        set_economy_status(not get_economy_status())
        await admin_panel(update, context)
    elif data == "admin_del_logger":
        delete_logger_group()
        await q.answer("🗑 Logger Deleted!")
        await admin_panel(update, context)
    elif data == "admin_wipe_ask":
        kb = [[InlineKeyboardButton("⚠️ CONFIRM WIPE", callback_data="admin_wipe_confirm")], [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]]
        await q.edit_message_text("☢️ **Database Wipe?** This cannot be undone!", reply_markup=InlineKeyboardMarkup(kb))
    elif data == "admin_wipe_confirm":
        wipe_database()
        await q.edit_message_text("💀 Database Wiped!")
    elif data == "admin_back":
        await admin_panel(update, context)
    elif data == "admin_close":
        await q.message.delete()
        if user_id in ADMIN_INPUT_STATE: del ADMIN_INPUT_STATE[user_id]

# --- 3. INPUT HANDLER ---
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) != str(OWNER_ID): return False
    state = ADMIN_INPUT_STATE.get(user_id)
    if not state: return False

    msg = update.message
    text = msg.text.strip() if msg.text else None

    # 🔥 1. BROADCAST LOGIC (ANY MEDIA) 🔥
    if state == 'broadcast':
        users = list(users_col.find({}))
        groups = list(groups_col.find({}))
        count = 0
        status_msg = await msg.reply_text("📢 Sending...")
        for chat in users + groups:
            try: 
                await context.bot.copy_message(chat_id=chat["_id"], from_chat_id=msg.chat_id, message_id=msg.message_id)
                count += 1
            except: pass
        await status_msg.edit_text(f"✅ Sent to {count} chats!")
        del ADMIN_INPUT_STATE[user_id]
        return True

    if not text: return False

    # 🔥 2. CHAT KEYS 🔥
    if state == 'add_key':
        if add_api_key(text): await msg.reply_text("✅ Chat Key Added!")
        else: await msg.reply_text("⚠️ Exists!")
    
    elif state == 'del_key':
        if remove_api_key(text): await msg.reply_text("🗑 Chat Key Deleted!")
        else: await msg.reply_text("❌ Not Found.")

    # 🔥 3. GAME KEYS 🔥
    elif state == 'add_game_key':
        if add_game_key(text): await msg.reply_text("✅ Game Key Added!")
        else: await msg.reply_text("⚠️ Exists!")

    elif state == 'del_game_key':
        if remove_game_key(text): await msg.reply_text("🗑 Game Key Deleted!")
        else: await msg.reply_text("❌ Not Found.")

    # 🔥 4. STICKER PACKS 🔥
    elif state == 'add_pack':
        pname = text.split('/')[-1]
        try:
            await context.bot.get_sticker_set(pname)
            if add_sticker_pack(pname): await msg.reply_text(f"✅ Pack Added: `{pname}`")
            else: await msg.reply_text("⚠️ Already Exists!")
        except: await msg.reply_text("❌ Invalid Pack!")
    
    elif state == 'del_pack':
        if remove_sticker_pack(text): await msg.reply_text("🗑 Pack Deleted!")
        else: await msg.reply_text("❌ Not Found.")

    # 🔥 5. MONEY & OTHERS 🔥
    elif state in ['add_money', 'take_money']:
        try:
            parts = text.split()
            tid, amt = int(parts[0]), int(parts[1])
            if state == 'take_money': amt = -amt
            update_balance(tid, amt)
            await msg.reply_text("✅ Balance Updated!")
        except: await msg.reply_text("❌ Error! Format: `ID Amount` ")

    elif state == 'create_code':
        try:
            parts = text.split()
            codes_col.insert_one({"code": parts[0], "amount": int(parts[1]), "limit": int(parts[2]), "redeemed_by": []})
            await msg.reply_text(f"🎁 Code Created: `{parts[0]}`")
        except: await msg.reply_text("❌ Error!")

    elif state == 'waiting_logger_id':
        try:
            set_logger_group(int(text))
            await msg.reply_text(f"✅ Logger Set: `{text}`")
        except: await msg.reply_text("❌ Invalid ID")

    del ADMIN_INPUT_STATE[user_id]
    return True
