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

# নিজের Telegram numeric ID
ADMIN_ID = 5196850561

admin_mode = False

# ---------- WEB ----------

app = Flask(__name__)

@app.route("/")
def home():
    return "Fast Proxy Support Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )

# ---------- COMMANDS ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Welcome 👋\nSend your issue."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "/start\n/help\n/admin_on\n/admin_off"
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

# ---------- MAIN MESSAGE ----------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    user = update.effective_user
    text = update.message.text

    # Forward message to admin
    forward_text = f"""
New User Message

User ID: {user.id}
Name: {user.first_name}

Message:
{text}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=forward_text
    )

    if admin_mode:
        return

    msg = text.lower()

    if "proxy" in msg:

        reply = """
Proxy problem?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network
"""

    elif "payment" in msg:

        reply = """
Payment issue?

Send screenshot
Transaction ID
"""

    elif "ip" in msg:

        reply = """
Try IP rotate.
Reconnect proxy.
"""

    else:

        reply = """
Please explain your issue clearly.
"""

    await update.message.reply_text(
        reply
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
