import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("8711495656:AAGj3qM8puS24eAIHf8vJuwvSTl0HCC5ioo")

admin_mode = False

async def admin_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_mode
    admin_mode = True
    await update.message.reply_text("Admin mode ON. Auto reply disabled.")

async def admin_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_mode
    admin_mode = False
    await update.message.reply_text("Admin mode OFF. Auto reply enabled.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if admin_mode:
        return

    msg = update.message.text.lower()

    if "proxy" in msg and ("not working" in msg or "kaj kortese na" in msg):
        reply = (
            "Proxy problem? Try:\n"
            "1. Restart network\n"
            "2. Rotate IP\n"
            "3. Check package expiry\n"
            "4. Try another network"
        )
    elif "payment" in msg:
        reply = "Payment methods: Bkash, Nagad, Binance, Crypto"
    else:
        reply = "Please explain your problem."

    await update.message.reply_text(reply)

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("admin_on", admin_on))
app.add_handler(CommandHandler("admin_off", admin_off))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()
