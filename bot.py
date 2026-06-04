import os
import asyncio
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# নিজের Telegram numeric ID বসাও
ADMIN_ID = 123456789

admin_mode = False

# ---------- WEB ----------

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(
        host="0.0.0.0",
        port=port
    )

# ---------- COMMANDS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Welcome 👋 Send your issue."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "/admin_on\n"
        "/admin_off\n"
        "/reply USER_ID message"
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

# ---------- MANUAL REPLY ----------

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(context.args[0])

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

    except:

        await update.message.reply_text(
            "Use:\n/reply USER_ID message"
        )

# ---------- AUTO REPLY ----------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    user = update.effective_user

    text = update.message.text

    msg_lower = text.lower()

    if admin_mode:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
Admin Mode Message

User: {user.first_name}
ID: {user.id}

{text}
"""
        )

        return

    # Generate auto reply

    if "proxy" in msg_lower:

        reply = """
Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network
"""

    elif "payment" in msg_lower:

        reply = """
Payment issue?

Send:

• Screenshot
• Transaction ID
"""

    elif "ip" in msg_lower:

        reply = """
Rotate IP once
Reconnect proxy
"""

    else:

        reply = """
Please explain your issue clearly.
"""

    # Send auto reply

    await update.message.reply_text(
        reply
    )

    # Send log to admin

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""
User: {user.first_name}
ID: {user.id}

Message:
{text}

Bot Reply:
{reply}
"""
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
