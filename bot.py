import os
import asyncio
from threading import Thread
from flask import Flask

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 5196850561   # নিজের Telegram ID

admin_mode = False
reply_mode = {}

# ---------------- WEB ----------------

web = Flask(__name__)

@web.route("/")
def home():
    return "Running"

def run_web():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    web.run(
        host="0.0.0.0",
        port=port
    )

# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = ReplyKeyboardMarkup(

        [
            ["/help"],
            ["/admin_on", "/admin_off"]
        ],

        resize_keyboard=True

    )

    await update.message.reply_text(

        "Hello 👋 Send your problem.",

        reply_markup=keyboard

    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

"""
/admin_on
/admin_off
/cancel_reply
"""

)

async def admin_on(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    if update.effective_user.id != ADMIN_ID:
        return

    admin_mode = True

    await update.message.reply_text(
        "Admin mode ON"
    )

async def admin_off(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    if update.effective_user.id != ADMIN_ID:
        return

    admin_mode = False

    await update.message.reply_text(
        "Admin mode OFF"
    )

async def cancel_reply(update: Update, context):

    if update.effective_user.id in reply_mode:

        del reply_mode[
            update.effective_user.id
        ]

    await update.message.reply_text(
        "Reply mode OFF"
    )

# ---------------- REPLY BUTTON ----------------

async def quick_reply(update, context):

    query = update.callback_query

    await query.answer()

    user_id = int(

        query.data.replace(
            "reply_",
            ""
        )

    )

    reply_mode[
        query.from_user.id
    ] = user_id

    await query.message.reply_text(

f"""
Reply mode ON ✅

Target User:

{user_id}

Now send text/photo.

Use /cancel_reply to stop
"""

)

# ---------------- MAIN HANDLER ----------------

async def handle(update: Update, context):

    global admin_mode

    user = update.effective_user

    full_name = user.full_name

    # -------- ADMIN REPLY MODE --------

    if user.id == ADMIN_ID:

        if user.id in reply_mode:

            target = reply_mode[
                user.id
            ]

            # photo

            if update.message.photo:

                file_id = update.message.photo[-1].file_id

                await context.bot.send_photo(

                    chat_id=target,

                    photo=file_id,

                    caption=update.message.caption

                )

                await update.message.reply_text(
                    "Photo Sent ✅"
                )

                return

            # text

            if update.message.text:

                await context.bot.send_message(

                    chat_id=target,

                    text=update.message.text

                )

                await update.message.reply_text(
                    "Reply Sent ✅"
                )

                return

    # -------- USER PHOTO --------

    if update.message.photo:

        buttons = InlineKeyboardMarkup(

            [[

                InlineKeyboardButton(

                    "Reply",

                    callback_data=f"reply_{user.id}"

                )

            ]]

        )

        file_id = update.message.photo[-1].file_id

        await context.bot.send_photo(

            chat_id=ADMIN_ID,

            photo=file_id,

            caption=f"""

👤 {full_name}

ID:

{user.id}

Photo Received
""",

            reply_markup=buttons

        )

        return

    # -------- USER TEXT --------

    text = update.message.text

    msg_lower = text.lower()

    is_bangla = any(

        "\u0980" <= ch <= "\u09FF"

        for ch in text

    )

    if "proxy" in msg_lower:

        if is_bangla:

            reply = """
Proxy সমস্যা?

1. Network restart করুন
2. IP rotate করুন
3. Expiry check করুন
"""

        else:

            reply = """
Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
"""

    else:

        if is_bangla:

            reply = "সমস্যাটা বিস্তারিত বলুন"

        else:

            reply = "Please explain clearly."

    await update.message.reply_text(
        reply
    )

    buttons = InlineKeyboardMarkup(

        [[

            InlineKeyboardButton(

                "Reply",

                callback_data=f"reply_{user.id}"

            )

        ]]

    )

    await context.bot.send_message(

        chat_id=ADMIN_ID,

        text=f"""

👤 User:

{full_name}

ID:

{user.id}

Message:

{text}

Bot Reply:

{reply}
""",

        reply_markup=buttons

    )

# ---------------- MAIN ----------------

async def main():

    Thread(

        target=run_web,

        daemon=True

    ).start()

    app = Application.builder().token(

        BOT_TOKEN

    ).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_cmd
        )
    )

    app.add_handler(
        CommandHandler(
            "admin_on",
            admin_on
        )
    )

    app.add_handler(
        CommandHandler(
            "admin_off",
            admin_off
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
            quick_reply
        )
    )

    app.add_handler(

        MessageHandler(

            filters.ALL,

            handle

        )

    )

    await app.initialize()

    await app.start()

    await app.updater.start_polling()

    while True:

        await asyncio.sleep(
            3600
        )

if __name__ == "__main__":

    asyncio.run(
        main()
    )
