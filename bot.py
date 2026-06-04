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
    ContextTypes,
    CallbackQueryHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 5196850561  # নিজের Telegram numeric ID বসাও

admin_mode = False

# ---------- WEB ----------

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running"

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

# ---------- COMMANDS ----------

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
/start
/help
/admin_on
/admin_off
/reply USER_ID message
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

# ---------- QUICK REPLY ----------

async def quick_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.data.replace(
        "reply_",
        ""
    )

    await query.message.reply_text(

        f"/reply {user_id} your_message"

    )

# ---------- MANUAL REPLY ----------

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(
            context.args[0]
        )

        text = " ".join(
            context.args[1:]
        )

        await context.bot.send_message(

            chat_id=user_id,

            text=text

        )

        await update.message.reply_text(
            "Reply Sent ✅"
        )

    except Exception as e:

        await update.message.reply_text(
            f"Failed: {e}"
        )

# ---------- MAIN MESSAGE ----------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    user = update.effective_user

    text = update.message.text

    msg_lower = text.lower()

    is_bangla = any(

        "\u0980" <= ch <= "\u09FF"

        for ch in text

    )

    if admin_mode:

        await context.bot.send_message(

            chat_id=ADMIN_ID,

            text=f"""

Admin Mode

User:
{user.full_name}

ID:
{user.id}

{text}
"""

        )

        return

    # AUTO REPLY

    if "proxy" in msg_lower:

        if is_bangla:

            reply = """
Proxy সমস্যা?

1. Network restart করুন
2. IP rotate করুন
3. Expiry check করুন
4. অন্য network try করুন
"""

        else:

            reply = """
Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network
"""

    elif "payment" in msg_lower:

        if is_bangla:

            reply = """
Payment problem?

Screenshot দিন
Transaction ID দিন
"""

        else:

            reply = """
Payment issue?

Send screenshot
Send transaction ID
"""

    else:

        if is_bangla:

            reply = "সমস্যাটা বিস্তারিত বলুন।"

        else:

            reply = "Please explain your issue clearly."

    await update.message.reply_text(
        reply
    )

    buttons = InlineKeyboardMarkup(

        [

            [

                InlineKeyboardButton(

                    "Reply",

                    callback_data=f"reply_{user.id}"

                )

            ]

        ]

    )

    try:

        await context.bot.send_message(

            chat_id=ADMIN_ID,

            text=f"""
👤 User:
{user.full_name}

🆔 ID:
`{user.id}`

📩 Message:
{text}

🤖 Bot Reply:
{reply}
""",

            parse_mode="Markdown",

            reply_markup=buttons

        )

    except Exception as e:

        print(
            e
        )

# ---------- MAIN ----------

async def main():

    Thread(

        target=run_web,

        daemon=True

    ).start()

    app_bot = Application.builder().token(

        BOT_TOKEN

    ).build()

    app_bot.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app_bot.add_handler(
        CommandHandler(
            "help",
            help_cmd
        )
    )

    app_bot.add_handler(
        CommandHandler(
            "admin_on",
            admin_on
        )
    )

    app_bot.add_handler(
        CommandHandler(
            "admin_off",
            admin_off
        )
    )

    app_bot.add_handler(
        CommandHandler(
            "reply",
            reply_cmd
        )
    )

    app_bot.add_handler(
        CallbackQueryHandler(
            quick_reply
        )
    )

    app_bot.add_handler(

        MessageHandler(

            filters.TEXT & ~filters.COMMAND,

            handle

        )

    )

    await app_bot.initialize()

    await app_bot.start()

    await app_bot.updater.start_polling()

    while True:

        await asyncio.sleep(
            3600
        )

if __name__ == "__main__":

    asyncio.run(
        main()
    )
