import os
import asyncio
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
ADMIN_ID = 5196850561   # নিজের admin id

reply_mode = {}

# ---------- Flask ----------
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Hello!\n\n"
        "Send your problem.\n\n"
        "📹 Tutorial video থাকলে mention করুন."
    )

    await update.message.reply_text(text)


async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    reply_mode.pop(ADMIN_ID, None)

    await update.message.reply_text(
        "❌ Reply mode OFF"
    )


# ---------- Reply Button ----------
async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    target = int(query.data.split("_")[1])

    reply_mode[ADMIN_ID] = target

    await query.message.reply_text(
        f"✅ Reply mode ON\n\n"
        f"Target User:\n{target}\n\n"
        f"Now send text/photo\n"
        f"/cancel_reply"
    )


# ---------- Main Message Handler ----------
async def all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    uid = user.id
    fullname = user.full_name

    text = update.message.text or ""

    print(f"NEW MESSAGE => {uid}: {text}")

    # Admin Reply Mode
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
                f"❌ Error:\n{e}"
            )

        return


    lower = text.lower()

    # Auto replies
    if any(x in lower for x in [
        "proxy",
        "kaj kore na",
        "dead",
        "not working",
        "problem"
    ]):

        bot_reply = (
            "🤖 Proxy issue?\n\n"
            "1. Restart network\n"
            "2. Rotate IP\n"
            "3. Check package expiry\n"
            "4. Try another network\n\n"
            "📹 Tutorial video থাকলে দেখুন."
        )

    elif len(text) <= 3:

        bot_reply = (
            "Please explain your issue clearly."
        )

    else:

        bot_reply = (
            "Support received ✅\n"
            "Admin will review shortly."
        )

    await update.message.reply_text(bot_reply)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "Reply",
                callback_data=f"reply_{uid}"
            )
        ]
    ])

    admin_text = (
        f"👤 User:\n"
        f"{fullname}\n\n"
        f"🆔 ID:\n"
        f"{uid}\n\n"
        f"📩 Message:\n"
        f"{text}\n\n"
        f"🤖 Bot Reply:\n"
        f"{bot_reply}"
    )

    try:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=keyboard
        )

    except Exception as e:

        print("ADMIN SEND ERROR:", e)


# ---------- Photo ----------
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

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
                f"❌ {e}"
            )


# ---------- Main ----------
async def main():

    app = Application.builder().token(BOT_TOKEN).build()

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
            photo_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            all_messages
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    print("BOT STARTED ✅")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    asyncio.run(main())
