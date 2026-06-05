import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "8711495656:AAEbT3-I_xrTvVeZFkx25FcODdPbgHOVx6A"
ADMIN_ID = 5196850561   # তোমার admin id

reply_mode = {}

# ============== FIX EVENT LOOP ==============
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# ============== FLASK KEEP ALIVE ==============
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# ============== AUTO REPLY ==============
def auto_reply(text):

    msg = text.lower()

    if any(x in msg for x in ["proxy", "dead", "kaj kortese na", "not working"]):
        return """🤖 Proxy issue?

1. Restart network
2. Rotate IP
3. Check package expiry
4. Try another network

🎥 Tutorial video থাকলে দেখুন।"""

    if any(x in msg for x in ["hello", "hi", "hey", "হাই"]):
        return "👋 Hello! Please explain your issue clearly."

    return "📝 Please explain your issue clearly."

# ============== START ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Support received ✅\nAdmin will review shortly."
    )

# ============== CALLBACK ==============
async def reply_button(update: Update, context):

    query = update.callback_query
    await query.answer()

    uid = int(query.data.split("_")[1])

    reply_mode[ADMIN_ID] = uid

    await query.message.reply_text(
        f"Reply mode ON ✅\n\nTarget User:\n{uid}\n\nNow send text/photo.\n\nUse /cancel_reply"
    )

# ============== CANCEL ==============
async def cancel_reply(update, context):

    reply_mode.pop(ADMIN_ID, None)

    await update.message.reply_text(
        "Reply mode OFF ❌"
    )

# ============== MESSAGE ==============
async def messages(update: Update, context):

    user = update.effective_user
    uid = user.id
    text = update.message.text if update.message.text else ""

    # admin reply mode
    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        try:

            if update.message.photo:

                file = update.message.photo[-1].file_id

                await context.bot.send_photo(
                    chat_id=target,
                    photo=file,
                    caption=update.message.caption
                )

                await update.message.reply_text(
                    "Photo Sent ✅"
                )

            else:

                await context.bot.send_message(
                    chat_id=target,
                    text=text
                )

                await update.message.reply_text(
                    "Reply Sent ✅"
                )

        except Exception as e:

            await update.message.reply_text(
                f"Error:\n{e}"
            )

        return

    # user auto reply
    bot_reply = auto_reply(text)

    await update.message.reply_text(bot_reply)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Reply",
            callback_data=f"reply_{uid}"
        )]
    ])

    admin_text = f"""
👤 User:
{user.full_name}

🆔 ID:
{uid}

📩 Message:
{text}

🤖 Bot Reply:

{bot_reply}
"""

    await context.bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=keyboard
    )

# ============== PHOTO ==============
async def photos(update: Update, context):

    uid = update.effective_user.id

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        file = update.message.photo[-1].file_id

        await context.bot.send_photo(
            target,
            file,
            caption=update.message.caption
        )

        await update.message.reply_text(
            "Photo Sent ✅"
        )

        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Reply",
            callback_data=f"reply_{uid}"
        )]
    ])

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"""
👤 User:
{update.effective_user.full_name}

🆔 ID:
{uid}

📷 User sent photo
""",
        reply_markup=keyboard
    )

# ============== MAIN ==============
def main():

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler(
            "cancel_reply",
            cancel_reply
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            reply_button
        )
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photos
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            messages
        )
    )

    print("BOT STARTED ✅")

    app.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    main()
