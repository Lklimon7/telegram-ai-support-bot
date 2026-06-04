import os
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

admin_mode = False

# -------- KEEP ALIVE WEB SERVER --------

app = Flask(__name__)

@app.route("/")
def home():
    return "Fast Proxy Support Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web).start()

# -------- COMMANDS --------

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

# -------- AUTO REPLY --------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_mode

    if admin_mode:
        return

    text = update.message.text.lower()

    if "proxy kaj kortese na" in text or "proxy not working" in text:
        msg = """Proxy problem? Try:

1. Restart network
2. Rotate IP
3. Check package expiry
4. Try another network"""
    
    elif "proxy" in text:
        msg = """Please explain your proxy issue.

Examples:
• Proxy setup
• IP change
• Recharge issue
• Connection problem"""

    else:
        msg = """Please explain your problem.

Examples:
• Proxy setup
• Payment issue
• Recharge issue
• IP problem"""

    await update.message.reply_text(msg)

# -------- MAIN --------

def main():
    keep_alive()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Welcome to Fast Proxy Support")))
    application.add_handler(CommandHandler("admin_on", admin_on))
    application.add_handler(CommandHandler("admin_off", admin_off))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle)
    )

    print("Bot Running...")
    application.run_polling()

if __name__ == "__main__":
    main()
