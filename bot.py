import os
import threading
from flask import Flask
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8711495656:AAEbT3-I_xrTvVeZFkx25FcODdPbgHOVx6A"
ADMIN_ID = 5196850561

reply_mode = {}

# ---------------- WEB ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )

# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Hello!\nSend your problem."
    )

async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    reply_mode.pop(ADMIN_ID, None)

    await update.message.reply_text(
        "❌ Reply mode OFF"
    )

# ---------------- BUTTON ----------------

async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    target = int(
        query.data.replace(
            "reply_",
            ""
        )
    )

    reply_mode[ADMIN_ID] = target

    await query.message.reply_text(
        f"✅ Reply Mode ON\n\n"
        f"Target: {target}\n\n"
        f"Send text/photo.\n"
        f"/cancel_reply"
    )

# ---------------- PHOTO ----------------

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in reply_mode:
        return

    target = reply_mode[ADMIN_ID]

    try:

        photo = update.message.photo[-1]

        await context.bot.send_photo(
            chat_id=target,
            photo=photo.file_id,
            caption=update.message.caption
        )

        await update.message.reply_text(
            "✅ Photo Sent"
        )

    except Exception as e:

        await update.message.reply_text(
            str(e)
        )

# ---------------- MESSAGE ----------------

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    uid = user.id
    name = user.full_name

    text = update.message.text or ""

    print(
        f"MSG {uid}: {text}"
    )

    # ADMIN REPLY MODE

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        try:

            await context.bot.send_message(
                chat_id=target,
                text=text
            )

            await update.message.reply_text(
                "✅ Reply Sent"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ {e}"
            )

        return

    lower = text.lower()

    # AUTO REPLY

    if any(
        x in lower for x in
        [
            "proxy",
            "kaj kore na",
            "dead",
            "not working"
        ]
    ):

        bot_reply = (
            "🤖 Proxy issue?\n\n"
            "1. Restart network\n"
            "2. Rotate IP\n"
            "3. Check package expiry\n"
            "4. Try another network\n\n"
            "📹 Check tutorial video if available."
        )

    elif lower in [
        "hi",
        "hello",
        "hey",
        "হাই"
    ]:

        bot_reply = (
            "👋 Hello!\n"
            "Please explain your issue."
        )

    else:

        bot_reply = (
            "✅ Support received.\n"
            "Admin will review shortly."
        )

    await update.message.reply_text(
        bot_reply
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Reply",
                callback_data=f"reply_{uid}"
            )
        ]
    ])

    admin_text = (

        f"👤 User:\n{name}\n\n"
        f"🆔 ID:\n{uid}\n\n"
        f"📩 Message:\n{text}\n\n"
        f"🤖 Reply:\n{bot_reply}"

    )

    try:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=keyboard
        )

    except Exception as e:

        print(
            "ADMIN ERROR:",
            e
        )

# ---------------- MAIN ----------------

def main():

    thread = threading.Thread(
        target=run_web
    )

    thread.daemon = True
    thread.start()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
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
            photo_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            message_handler
        )
    )

    print(
        "BOT STARTED ✅"
    )

    app.run_polling(
        drop_pending_updates=True
    )

if __name__ == "__main__":

    main()
