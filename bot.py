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

# নিজের Telegram ID বসাও
ADMIN_ID = 5196850561

admin_mode = False

# ---------------- WEB SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello 👋 Send your problem."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start bot\n"
        "/help - Commands\n"
        "/admin_on - Disable auto reply\n"
        "/admin_off - Enable auto reply"
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

# ---------------- MESSAGE HANDLER ----------------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    if admin_mode:
        return

    text = update.message.text.lower()

    print(
        f"{update.effective_user.id} : {text}"
    )

    if "proxy" in text:

        msg = """
Proxy problem? Try:

1. Restart network
2. Rotate IP
3. Check package expiry
4. Try another network
"""

    elif "price" in text:

        msg = "Please check package menu."

    elif "expire" in text:

        msg = "Please check package expiry."

    elif "refund" in text:

        msg = "Contact support for refund."

    else:

        msg = "Please explain your problem."

    await update.message.reply_text(msg)

# ---------------- MAIN ----------------

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
    asyncio.run(main())
