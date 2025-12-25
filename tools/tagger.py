import random
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest, Forbidden, TelegramError

# Global variables
active_tag_sessions = {}

# EMOJI and MESSAGES (same as before)
EMOJI = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐", "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤", "💓💕💞💗💖", "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️", "🧋🥤🧋🥛🍷", "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙", "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️", "🌷🏵️🌸🌺💐", "💮🌼🌻🍀🍁", "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦", "🐷🐹🐭🐨🐻‍❄️", "🦋🐇🐀🐈🐈‍⬛", "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇", "🍴🍽️🔪🍶🥃", "🕌🏰🏩⛩️🏩", "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲", "🎄🎋🎍🎑🎎", "🦅🦜🕊️🦤🦢", "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳", "🐔🐟🐠🐡🦐", "🦩🦀🦑🐙🦪", "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨", " 🥬🍉🧁🧇",
]

TAGMES = [
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ 🌚**",
    "**➠ ᴄʜᴜᴘ ᴄʜᴀᴘ sᴏ ᴊᴀ 🙊**",
    "**➠ ᴘʜᴏɴᴇ ʀᴀᴋʜ ᴋᴀʀ sᴏ ᴊᴀ, ɴᴀʜɪ ᴛᴏ ʙʜᴏᴏᴛ ᴀᴀ ᴊᴀʏᴇɢᴀ..👻**",
    "**➠ ᴀᴡᴇᴇ ʙᴀʙᴜ sᴏɴᴀ ᴅɪɴ ᴍᴇɪɴ ᴋᴀʀ ʟᴇɴᴀ ᴀʙʜɪ sᴏ ᴊᴀᴏ..?? 🥲**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ᴀᴘɴᴇ ɢғ sᴇ ʙᴀᴀᴛ ᴋʀ ʀʜᴀ ʜ ʀᴀᴊᴀɪ ᴍᴇ ɢʜᴜs ᴋᴀʀ, sᴏ ɴᴀʜɪ ʀᴀʜᴀ 😜**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴅᴇᴋʜᴏ ᴀᴘɴᴇ ʙᴇᴛᴇ ᴋᴏ ʀᴀᴀᴛ ʙʜᴀʀ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ʜᴀɪ 🤭**",
    "**➠ ᴊᴀɴᴜ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ..?? 🌠**",
    "**➠ ɢɴ sᴅ ᴛᴄ.. 🙂**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ ᴛᴀᴋᴇ ᴄᴀʀᴇ..?? ✨**",
    "**➠ ʀᴀᴀᴛ ʙʜᴜᴛ ʜᴏ ɢʏɪ ʜᴀɪ sᴏ ᴊᴀᴏ, ɢɴ..?? 🌌**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ 11 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ɴᴀʜɪ sᴏ ɴᴀʜɪ ʀᴀʜᴀ 🕦**",
    "**➠ ᴋᴀʟ sᴜʙʜᴀ sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴀᴋ ᴊᴀɢ ʀʜᴇ ʜᴏ 🏫**",
    "**➠ ʙᴀʙᴜ, ɢᴏᴏᴅ ɴɪɢʜᴛ sᴅ ᴛᴄ..?? 😊**",
    "**➠ ᴀᴀᴊ ʙʜᴜᴛ ᴛʜᴀɴᴅ ʜᴀɪ, ᴀᴀʀᴀᴍ sᴇ ᴊᴀʟᴅɪ sᴏ ᴊᴀᴛɪ ʜᴏᴏɴ 🌼**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🌷**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ sᴏɴᴇ, ɢɴ sᴅ ᴛᴄ 🏵️**",
    "**➠ ʜᴇʟʟᴏ ᴊɪ ɴᴀᴍᴀsᴛᴇ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🍃**",
    "**➠ ʜᴇʏ, ʙᴀʙʏ ᴋᴋʀʜ..? sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ ☃️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ, ʙʜᴜᴛ ʀᴀᴀᴛ ʜᴏ ɢʏɪ..? ⛄**",
    "**➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ ʀᴏɴᴇ, ɪ ᴍᴇᴀɴ sᴏɴᴇ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ 😁**",
    "**➠ ᴍᴀᴄʜʜᴀʟɪ ᴋᴏ ᴋᴇʜᴛᴇ ʜᴀɪ ғɪsʜ, ɢᴏᴏᴅ ɴɪɢʜᴛ ᴅᴇᴀʀ ᴍᴀᴛ ᴋʀɴᴀ ᴍɪss, ᴊᴀ ʀʜɪ sᴏɴᴇ 🌄**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ʙʀɪɢʜᴛғᴜʟʟ ɴɪɢʜᴛ 🤭**",
    "**➠ ᴛʜᴇ ɴɪɢʜᴛ ʜᴀs ғᴀʟʟᴇɴ, ᴛʜᴇ ᴅᴀʏ ɪs ᴅᴏɴᴇ,, ᴛʜᴇ ᴍᴏᴏɴ ʜᴀs ᴛᴀᴋᴇɴ ᴛʜᴇ ᴘʟᴀᴄᴇ ᴏғ ᴛʜᴇ sᴜɴ... 😊**",
    "**➠ ᴍᴀʏ ᴀʟʟ ʏᴏᴜʀ ᴅʀᴇᴀᴍs ᴄᴏᴍᴇ ᴛʀᴜᴇ ❤️**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴘʀɪɴᴋʟᴇs sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ 💚**",
    "**➠ ɢᴏᴏᴅ ɴɪɢʜᴛ, ɴɪɴᴅ ᴀᴀ ʀʜɪ ʜᴀɪ 🥱**",
    "**➠ ᴅᴇᴀʀ ғʀɪᴇɴᴅ ɢᴏᴏᴅ ɴɪɢʜᴛ 💤**",
    "**➠ ʙᴀʙʏ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ 🥰**",
    "**➠ ɪᴛɴɪ ʀᴀᴀᴛ ᴍᴇ ᴊᴀɢ ᴋᴀʀ ᴋʏᴀ ᴋᴀʀ ʀʜᴇ ʜᴏ sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 😜**",
    "**➠ ᴄʟᴏsᴇ ʏᴏᴜʀ ᴇʏᴇs sɴᴜɢɢʟᴇ ᴜᴘ ᴛɪɢʜᴛ,, ᴀɴᴅ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ᴀɴɢᴇʟs, ᴡɪʟʟ ᴡᴀᴛᴄʜ ᴏᴠᴇʀ ʏᴏᴜ ᴛᴏɴɪɢʜᴛ... 💫**",
]

VC_TAG = [
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋᴇsᴇ ʜᴏ 🐱**",
    "**➠ ɢᴍ, sᴜʙʜᴀ ʜᴏ ɢʏɪ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 🌤️**",
    "**➠ ɢᴍ ʙᴀʙʏ, ᴄʜᴀɪ ᴘɪ ʟᴏ ☕**",
    "**➠ ᴊᴀʟᴅɪ ᴜᴛʜᴏ, sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ 🏫**",
    "**➠ ɢᴍ, ᴄʜᴜᴘ ᴄʜᴀᴘ ʙɪsᴛᴇʀ sᴇ ᴜᴛʜᴏ ᴠʀɴᴀ ᴘᴀɴɪ ᴅᴀʟ ᴅᴜɴɢɪ 🧊**",
    "**➠ ʙᴀʙʏ ᴜᴛʜᴏ ᴀᴜʀ ᴊᴀʟᴅɪ ғʀᴇsʜ ʜᴏ ᴊᴀᴏ, ɴᴀsᴛᴀ ʀᴇᴀᴅʏ ʜᴀɪ 🫕**",
    "**➠ ᴏғғɪᴄᴇ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ ᴊɪ ᴀᴀᴊ, ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🏣**",
    "**➠ ɢᴍ ᴅᴏsᴛ, ᴄᴏғғᴇᴇ/ᴛᴇᴀ ᴋʏᴀ ʟᴏɢᴇ ☕🍵**",
    "**➠ ʙᴀʙʏ 8 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ, ᴀᴜʀ ᴛᴜᴍ ᴀʙʜɪ ᴛᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🕖**",
    "**➠ ᴋʜᴜᴍʙʜᴋᴀʀᴀɴ ᴋɪ ᴀᴜʟᴀᴅ ᴜᴛʜ ᴊᴀᴀ... ☃️**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ... 🌄**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴀᴠᴇ ᴀ ɢᴏᴏᴅ ᴅᴀʏ... 🪴**",
    "**➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙᴀʙʏ 😇**",
    "**➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ɴᴀʟᴀʏᴋ ᴀʙʜɪ ᴛᴀᴋ sᴏ ʀʜᴀ ʜᴀɪ... 😵‍💫**",
    "**➠ ʀᴀᴀᴛ ʙʜᴀʀ ʙᴀʙᴜ sᴏɴᴀ ᴋʀ ʀʜᴇ ᴛʜᴇ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴋ sᴏ ʀʜᴇ ʜᴏ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ... 😏**",
    "**➠ ʙᴀʙᴜ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴜᴛʜ ᴊᴀᴏ ᴀᴜʀ ɢʀᴏᴜᴘ ᴍᴇ sᴀʙ ғʀɪᴇɴᴅs ᴋᴏ ɢᴍ ᴡɪsʜ ᴋʀᴏ... 🌟**",
    "**➠ ᴘᴀᴘᴀ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜ ɴᴀʜɪ, sᴄʜᴏᴏʟ ᴋᴀ ᴛɪᴍᴇ ɴɪᴋᴀʟᴛᴀ ᴊᴀ ʀʜᴀ ʜᴀɪ... 🥲**",
    "**➠ ᴊᴀɴᴇᴍᴀɴ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋʏᴀ ᴋʀ ʀʜᴇ ʜᴏ ... 😅**",
    "**➠ ɢᴍ ʙᴇᴀsᴛɪᴇ, ʙʀᴇᴀᴋғᴀsᴛ ʜᴜᴀ ᴋʏᴀ... 🍳**",
]

# ==================== HELPER FUNCTIONS ====================
async def is_user_admin(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is admin"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def is_bot_admin(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot is admin in the group"""
    try:
        bot_id = context.bot.id
        chat_member = await context.bot.get_chat_member(chat_id, bot_id)
        return chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def get_all_members_as_admin(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Get ALL members when bot is admin"""
    members = []
    
    try:
        # First check if bot is admin
        if not await is_bot_admin(chat_id, context):
            print("❌ Bot is not admin, cannot get all members")
            return members
        
        print("✅ Bot is admin, attempting to get all members...")
        
        # Method 1: Try to get members using get_chat_members (if available)
        try:
            # This only works for small groups usually
            async for member in context.bot.get_chat_members(chat_id):
                if not member.user.is_bot:
                    members.append(member.user)
            print(f"✅ Method 1: Found {len(members)} members")
        except Exception as e:
            print(f"Method 1 failed: {e}")
        
        # Method 2: Get from chat administrators (always works for admins)
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            admin_ids = [m.user.id for m in members]
            
            for admin in admins:
                if not admin.user.is_bot and admin.user.id not in admin_ids:
                    members.append(admin.user)
            print(f"✅ Method 2: Added {len(admins)} admins")
        except Exception as e:
            print(f"Method 2 failed: {e}")
        
        # Method 3: Get from recent messages (500 messages)
        try:
            message_senders = set()
            async for message in context.bot.get_chat_history(chat_id, limit=500):
                if hasattr(message, 'from_user') and message.from_user:
                    user = message.from_user
                    if not user.is_bot and user.id not in [m.id for m in members]:
                        members.append(user)
                        message_senders.add(user.id)
            print(f"✅ Method 3: Added {len(message_senders)} recent message senders")
        except Exception as e:
            print(f"Method 3 failed: {e}")
        
        print(f"📊 Total unique members found: {len(members)}")
        
    except Exception as e:
        print(f"❌ Error getting members: {e}")
    
    return members

async def tag_all_members_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, tag_text: str, tag_type: str):
    """Tag all members when bot is admin"""
    try:
        # Send start message
        start_msg = await context.bot.send_message(
            chat_id,
            "👑 **ADMIN MODE ACTIVATED**\n"
            "🔍 Collecting ALL group members...\n"
            "⏳ This may take a while for large groups."
        )
        
        # Check if bot is admin
        if not await is_bot_admin(chat_id, context):
            await start_msg.edit_text(
                "❌ **Bot is not Admin!**\n"
                "Please make me admin to tag all members.\n"
                "Required permissions:\n"
                "• Delete messages\n"
                "• Invite users\n"
                "• Pin messages"
            )
            return
        
        # Get all members
        all_members = await get_all_members_as_admin(chat_id, context)
        
        if not all_members:
            await start_msg.edit_text(
                "❌ Could not collect members!\n"
                "Try these solutions:\n"
                "1. Make sure bot has admin rights\n"
                "2. Try in a smaller group first\n"
                "3. Use /tagtest to test"
            )
            return
        
        # Update start message
        await start_msg.edit_text(
            f"✅ **Found {len(all_members)} members!**\n"
            f"🎯 Starting to tag everyone...\n"
            f"⏳ Estimated time: {len(all_members) * 2} seconds\n"
            f"🛑 Use /tagstop to cancel"
        )
        
        # Initialize session
        active_tag_sessions[chat_id] = {
            "stop": False,
            "tagged": 0,
            "total": len(all_members),
            "failed": 0
        }
        
        tagged_count = 0
        failed_count = 0
        
        # Shuffle members for better distribution
        random.shuffle(all_members)
        
        # Tag each member
        for i, user in enumerate(all_members):
            # Check if should stop
            if active_tag_sessions[chat_id]["stop"]:
                break
            
            user_name = user.first_name or "User"
            user_id = user.id
            
            # Create tag message
            if tag_type == "gn":
                message = f"[{user_name}](tg://user?id={user_id}) {random.choice(TAGMES)}"
            elif tag_type == "gm":
                message = f"[{user_name}](tg://user?id={user_id}) {random.choice(VC_TAG)}"
            else:
                message = f"[{user_name}](tg://user?id={user_id}) {tag_text}"
            
            # Send tag
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                tagged_count += 1
                active_tag_sessions[chat_id]["tagged"] = tagged_count
                
            except Forbidden:
                # User blocked bot
                failed_count += 1
                active_tag_sessions[chat_id]["failed"] = failed_count
            except Exception as e:
                print(f"Error tagging {user_name}: {e}")
                failed_count += 1
                active_tag_sessions[chat_id]["failed"] = failed_count
            
            # Progress update every 15 users
            if (i + 1) % 15 == 0:
                progress = (
                    f"📊 **Progress: {i+1}/{len(all_members)}**\n"
                    f"✅ Tagged: {tagged_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"⏳ Remaining: {len(all_members) - (i+1)} users"
                )
                try:
                    await context.bot.send_message(chat_id, progress)
                except:
                    pass
            
            # Delay (adjust based on group size)
            delay = 1.5 if len(all_members) > 50 else 2.0
            await asyncio.sleep(delay)
        
        # Final message
        if active_tag_sessions[chat_id]["stop"]:
            final_msg = (
                f"🛑 **Tagging Stopped**\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ Tagged: {tagged_count} users\n"
                f"❌ Failed: {failed_count}\n"
                f"⏹️ Process was cancelled"
            )
        else:
            final_msg = (
                f"🎉 **TAGGING COMPLETE!**\n"
                f"━━━━━━━━━━━━━━\n"
                f"📊 **Final Statistics**\n"
                f"• Total Members Found: {len(all_members)}\n"
                f"• Successfully Tagged: {tagged_count}\n"
                f"• Failed: {failed_count}\n"
                f"• Success Rate: {(tagged_count/len(all_members))*100:.1f}%\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ **All available members have been tagged!**"
            )
        
        await context.bot.send_message(chat_id, final_msg, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        print(f"Admin tagging error: {e}")
        await context.bot.send_message(chat_id, f"❌ Error: {str(e)[:200]}")
    finally:
        if chat_id in active_tag_sessions:
            del active_tag_sessions[chat_id]

# ==================== COMMAND HANDLERS ====================
async def tag_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tagall command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    # Check if already running
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    # Check if user is admin
    if not await is_user_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Get tag text
    tag_text = ""
    if update.message.reply_to_message:
        tag_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    elif context.args:
        tag_text = " ".join(context.args)
    
    if not tag_text:
        await update.message.reply_text(
            "📝 Please provide text or reply to a message!\n"
            "Example: `/tagall Good Morning` or reply to a message with `/tagall`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Start background task
    asyncio.create_task(
        tag_all_members_admin(context, chat.id, tag_text, "custom")
    )
    
    await update.message.reply_text(
        f"🚀 **ADMIN TAG STARTED**\n\n"
        f"📝 Message: `{tag_text[:50]}...`\n"
        f"👑 Bot Admin Mode: **ACTIVE**\n"
        f"🔍 Collecting ALL members...\n"
        f"🛑 Use `/tagstop` to cancel",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_all_gm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gmtag command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    if not await is_user_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Start background task
    asyncio.create_task(
        tag_all_members_admin(context, chat.id, "", "gm")
    )
    
    await update.message.reply_text(
        "🌅 **GOOD MORNING TAG STARTED**\n\n"
        "👑 Bot Admin Mode: **ACTIVE**\n"
        "🔍 Tagging ALL members...\n"
        "🛑 Use `/tagstop` to cancel",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_all_gn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gntag command"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    if chat.id in active_tag_sessions:
        await update.message.reply_text("⚠️ Tagging is already running! Use /tagstop to stop.")
        return
    
    if not await is_user_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    # Start background task
    asyncio.create_task(
        tag_all_members_admin(context, chat.id, "", "gn")
    )
    
    await update.message.reply_text(
        "🌙 **GOOD NIGHT TAG STARTED**\n\n"
        "👑 Bot Admin Mode: **ACTIVE**\n"
        "🔍 Tagging ALL members...\n"
        "🛑 Use `/tagstop` to cancel",
        parse_mode=ParseMode.MARKDOWN
    )

async def tag_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test tag - tags 5 members"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    if not await is_user_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to use this command!")
        return
    
    await update.message.reply_text("🧪 Testing admin tag function...")
    
    try:
        # Get members
        members = await get_all_members_as_admin(chat.id, context)
        if not members:
            await update.message.reply_text("❌ No members found!")
            return
        
        # Take first 5 members
        members_to_tag = members[:5]
        
        tagged = 0
        for user_obj in members_to_tag:
            try:
                message = f"[{user_obj.first_name}](tg://user?id={user_obj.id}) Test tag from admin bot! 🎯"
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
                tagged += 1
                await asyncio.sleep(1)
            except:
                pass
        
        await update.message.reply_text(
            f"✅ **Test Complete!**\n"
            f"Tagged {tagged}/5 members successfully.\n"
            f"Total members found: {len(members)}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Test failed: {str(e)}")

async def check_bot_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot is admin"""
    chat = update.effective_chat
    
    if chat.type == 'private':
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    is_admin = await is_bot_admin(chat.id, context)
    
    if is_admin:
        await update.message.reply_text(
            "✅ **Bot is Admin!**\n"
            "👑 All tag commands will work properly.\n"
            "🔍 Can access all group members."
        )
    else:
        await update.message.reply_text(
            "❌ **Bot is NOT Admin!**\n"
            "Please make me admin with these permissions:\n"
            "• Delete messages\n"
            "• Invite users\n"
            "• Pin messages\n\n"
            "Without admin rights, I can only tag:\n"
            "• Other admins\n"
            "• Recent message senders"
        )

async def tag_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop tagging"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.id not in active_tag_sessions:
        await update.message.reply_text("ℹ️ No tagging process is running.")
        return
    
    if not await is_user_admin(chat.id, user.id, context):
        await update.message.reply_text("❌ You need to be an admin to stop tagging!")
        return
    
    active_tag_sessions[chat.id]["stop"] = True
    await update.message.reply_text("🛑 Stopping tagging process...")

async def tag_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check status"""
    chat = update.effective_chat
    
    if chat.id in active_tag_sessions:
        session = active_tag_sessions[chat.id]
        status_msg = (
            f"🔄 **Tagging in Progress**\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ Tagged: {session.get('tagged', 0)}\n"
            f"❌ Failed: {session.get('failed', 0)}\n"
            f"📊 Total: {session.get('total', 0)}\n"
            f"⏳ Progress: {(session.get('tagged', 0)/session.get('total', 1))*100:.1f}%\n"
            f"━━━━━━━━━━━━━━\n"
            f"👑 **Admin Mode: ACTIVE**"
        )
        await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("ℹ️ No active tagging session.")

# ==================== REGISTER HANDLERS ====================
def register_handlers(app: Application):
    """Register all handlers"""
    app.add_handler(CommandHandler("tagall", tag_all))
    app.add_handler(CommandHandler("gmtag", tag_all_gm))
    app.add_handler(CommandHandler("gntag", tag_all_gn))
    app.add_handler(CommandHandler("tagstop", tag_stop))
    app.add_handler(CommandHandler("tagstatus", tag_status))
    app.add_handler(CommandHandler("tagtest", tag_test))
    app.add_handler(CommandHandler("checkadmin", check_bot_admin))
    app.add_handler(CommandHandler("taghelp", tag_help))
    
    print("✅ Admin Tagger Plugin Loaded Successfully!")

async def tag_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
👑 **ADMIN TAGGER PLUGIN**

**For Group Admins Only:**
• `/tagall [text]` - Tag ALL members with custom text
• `/gmtag` - Good Morning tag for ALL members
• `/gntag` - Good Night tag for ALL members
• `/tagstop` - Stop ongoing tagging
• `/tagstatus` - Check tagging progress
• `/tagtest` - Test tag (tags 5 members)
• `/checkadmin` - Check if bot is admin
• `/taghelp` - Show this help

**REQUIREMENTS:**
1. 🤖 **Bot must be group admin**
2. 👮 **User must be admin to use commands**
3. ✅ **Bot needs these permissions:**
   • Delete messages
   • Invite users
   • Pin messages

**How it works when bot is admin:**
✅ Tags ALL group members (not just admins)
✅ Collects members from:
   • All chat members (admin access)
   • Administrators list
   • Recent message history
✅ Shows real-time progress
✅ Can be stopped anytime

**Note:**
• Large groups may take time (1.5s delay between tags)
• Some users may block the bot (will be skipped)
• Use `/tagtest` first to verify
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    print("👑 ADMIN TAGGER PLUGIN READY!")
