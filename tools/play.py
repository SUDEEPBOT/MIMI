from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes
from config import ASSISTANT_ID
from tools.stream import play_stream


async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    message = update.message

    if not context.args:
        return await message.reply_text(
            "<blockquote><b>❌ Usage:</b> <code>/play song name</code></blockquote>",
            parse_mode=ParseMode.HTML
        )

    # 🔐 Assistant presence check (ONLY THIS MUCH)
    try:
        assistant = await chat.get_member(int(ASSISTANT_ID))
        if assistant.status not in ["administrator", "member"]:
            raise Exception("Assistant not in group")
    except:
        return await message.reply_text(
            "<blockquote><b>❌ Assistant Missing</b></blockquote>\n"
            "Please add the assistant to this group and make it admin (Manage VC).",
            parse_mode=ParseMode.HTML
        )

    song_name = " ".join(context.args)
    status = await message.reply_text(
        f"<blockquote><b>🔍 Searching</b></blockquote>\n<code>{song_name}</code>",
        parse_mode=ParseMode.HTML
    )

    try:
        success, result = await play_stream(
            chat.id,
            song_name,
            song_name,
            0,
            user.first_name
        )

        if success:
            await status.edit_text(
                f"<blockquote><b>🎶 Now Playing</b></blockquote>\n\n"
                f"<b>Title:</b> {song_name}\n"
                f"<b>Requested by:</b> {user.first_name}",
                parse_mode=ParseMode.HTML
            )
        else:
            await status.edit_text(
                f"<blockquote><b>📌 Added to Queue</b></blockquote>\n"
                f"Position: <code>{result}</code>",
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        await status.edit_text(
            f"<blockquote><b>❌ Play Error</b></blockquote>\n<code>{e}</code>",
            parse_mode=ParseMode.HTML
        )


def register_handlers(app):
    app.add_handler(CommandHandler(["play", "p"], play_music))
