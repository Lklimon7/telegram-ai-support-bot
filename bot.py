import os
import asyncio
from threading import Thread
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

BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = 5196850561  # your telegram id

reply_mode = {}
admin_auto = False

# ================= WEB SERVER FOR RENDER =================

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello 👋 Send your problem."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = """
/start - Start bot
/help - Commands
/admin_on - Disable auto reply
/admin_off - Enable auto reply
/cancel_reply - Stop reply mode
"""
    await update.message.reply_text(txt)

async def admin_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_auto

    if update.effective_user.id != ADMIN_ID:
        return

    admin_auto = True
    await update.message.reply_text("Admin mode ON ✅")

async def admin_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_auto

    if update.effective_user.id != ADMIN_ID:
        return

    admin_auto = False
    await update.message.reply_text("Admin mode OFF ✅")

async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    reply_mode.pop(ADMIN_ID, None)

    await update.message.reply_text(
        "Reply mode OFF ❌"
    )

# ================= BUTTON =================

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("reply_"):
        uid = int(data.split("_")[1])

        reply_mode[ADMIN_ID] = uid

        await query.message.reply_text(
            f"Reply mode ON ✅\n\nTarget User:\n{uid}\n\nNow send text/photo.\n\nUse /cancel_reply"
        )

# ================= ADMIN FORWARD =================

async def send_to_admin(user, msg, bot_reply, context):

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "Reply",
            callback_data=f"reply_{user.id}"
        )]
    ])

    text = f"""
👤 User:
{user.full_name}

🆔 ID:
{user.id}

📩 Message:
{msg}

🤖 Bot Reply:

{bot_reply}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=keyboard
    )

# ================= AUTO REPLY =================

def detect_reply(msg):

    m = msg.lower()

    if "proxy" in m:
        return """Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network"""

    if any(x in m for x in [
        "hi","hello","hey","oi"
    ]):
        return "Please explain clearly."

    bangla = [
        "ভাই","কাজ","হচ্ছে","না","সমস্যা"
    ]

    if any(x in msg for x in bangla):
        return "সমস্যাটা বিস্তারিত বলুন"

    return "Please explain your issue clearly."

# ================= MESSAGE =================

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_auto

    uid = update.effective_user.id

    # ADMIN REPLY MODE

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        try:

            if update.message.photo:

                file = update.message.photo[-1].file_id

                await context.bot.send_photo(
                    target,
                    file,
                    caption=update.message.caption or ""
                )

            else:

                await context.bot.send_message(
                    target,
                    update.message.text
                )

            await update.message.reply_text(
                "Reply Sent ✅"
            )

        except Exception as e:

            await update.message.reply_text(
                f"Send Failed ❌\n{e}"
            )

        return

    if uid == ADMIN_ID:
        return

    text = update.message.text or ""

    if admin_auto:

        reply = "Support will reply soon."

    else:

        reply = detect_reply(text)

    await update.message.reply_text(reply)

    await send_to_admin(
        update.effective_user,
        text,
        reply,
        context
    )

# ================= PHOTO =================

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid == ADMIN_ID and ADMIN_ID in reply_mode:

        target = reply_mode[ADMIN_ID]

        try:

            photo_id = update.message.photo[-1].file_id

            await context.bot.send_photo(
                target,
                photo_id,
                caption=update.message.caption or ""
            )

            await update.message.reply_text(
                "Photo Sent ✅"
            )

        except Exception as e:

            await update.message.reply_text(
                str(e)
            )

# ================= MAIN =================

async def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler(
        "start", start
    ))

    app.add_handler(CommandHandler(
        "help", help_cmd
    ))

    app.add_handler(CommandHandler(
        "admin_on", admin_on
    ))

    app.add_handler(CommandHandler(
        "admin_off", admin_off
    ))

    app.add_handler(CommandHandler(
        "cancel_reply", cancel_reply
    ))

    app.add_handler(
        CallbackQueryHandler(button_click)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message
        )
    )

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":

    keep_alive()

    asyncio.run(main())
