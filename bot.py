import os
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

admin_mode = False

# ---------------- WEB SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Fast Proxy Support Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello 👋 I'm here to help.\nSend your issue."
    )

async def admin_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_mode
    admin_mode = True
    await update.message.reply_text(
        "Admin mode ON. Auto reply disabled."
    )

async def admin_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_mode
    admin_mode = False
    await update.message.reply_text(
        "Admin mode OFF. Auto reply enabled."
    )

# ---------------- AUTO REPLY ----------------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global admin_mode

    if admin_mode:
        return

    text = update.message.text.lower()

    if "proxy kaj kortese na" in text or "proxy not working" in text:
        reply = """Proxy problem? Try:

1. Restart network
2. Rotate IP
3. Check package expiry
4. Try another network"""

    elif "proxy" in text:
        reply = """Please explain your proxy issue.

Examples:
• Proxy setup
• Proxy not working
• IP change
• Recharge issue"""

    elif "payment" in text or "recharge" in text:
        reply = """Payment / Recharge issue?

Please send:
• Payment method
• Amount
• Transaction ID"""

    else:
        reply = """Please explain your problem.

Examples:
• Proxy setup
• Proxy not working
• Payment issue
• Recharge issue"""

    await update.message.reply_text(reply)

# ---------------- MAIN ----------------

def main():

    keep_alive()

    app_bot = Application.builder().token(BOT_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("admin_on", admin_on))
    app_bot.add_handler(CommandHandler("admin_off", admin_off))

    app_bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle
        )
    )

    print("Bot Running...")

    app_bot.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    main()
