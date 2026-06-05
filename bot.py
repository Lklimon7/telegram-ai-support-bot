import os
import asyncio
import threading

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

BOT_TOKEN = os.getenv("8711495656:AAEbT3-I_xrTvVeZFkx25FcODdPbgHOVx6A")
ADMIN_ID = 5196850561  # তোমার Admin ID দাও এখানে

reply_mode = {}

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot Running ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello!\n\nSend your problem.\nTutorial video থাকলে mention করুন."
    )


async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return

    reply_mode.pop(uid, None)

    await update.message.reply_text(
        "❌ Reply mode OFF"
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.replace("reply_", ""))

    reply_mode[ADMIN_ID] = user_id

    await query.message.reply_text(
        f"✅ Reply mode ON\n\nTarget User:\n{user_id}\n\nNow send text/photo.\n\nUse /cancel_reply"
    )


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    uid = user.id
    fullname = user.full_name

    msg = update.message.text or ""

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        try:
            await context.bot.send_message(
                chat_id=target,
                text=msg
            )

            await update.message.reply_text(
                "✅ Reply Sent"
            )

        except Exception as e:
            await update.message.reply_text(
                f"❌ Failed\n{e}"
            )

        return

    lower = msg.lower()

    if "proxy" in lower or "kaj kore na" in lower:

        bot_reply = (
            "🤖 Proxy issue?\n\n"
            "1. Restart network\n"
            "2. Rotate IP\n"
            "3. Check package expiry\n"
            "4. Try another network\n"
            "5. Tutorial video থাকলে দেখুন"
        )

    else:
        bot_reply = "Please explain your issue clearly."

    await update.message.reply_text(bot_reply)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Reply",
            callback_data=f"reply_{uid}"
        )]
    ])

    admin_text = f"""
👤 User:
{fullname}

🆔 ID:
{uid}

📩 Message:
{msg}

🤖 Bot Reply:

{bot_reply}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        reply_markup=keyboard
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        photo = update.message.photo[-1]

        try:

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
                f"❌ Failed\n{e}"
            )


async def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("cancel_reply", cancel_reply)
    )

    application.add_handler(
        CallbackQueryHandler(button_click)
    )

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            forward_to_admin
        )
    )

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    asyncio.run(main())
