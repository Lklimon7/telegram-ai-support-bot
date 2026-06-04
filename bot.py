import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5196850561   # replace with your telegram numeric id

reply_mode = {}

# ---------- START ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Hello! Send your problem."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

"""📌 Commands:

/start - Start bot
/help - Commands
/cancel_reply - Stop reply mode
"""
    )


async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    reply_mode.pop(
        ADMIN_ID,
        None
    )

    await update.message.reply_text(
        "❌ Reply mode OFF"
    )


# ---------- BUTTON ----------

async def quick_reply(update, context):

    query = update.callback_query

    await query.answer()

    target = int(
        query.data.replace(
            "reply_",
            ""
        )
    )

    reply_mode[
        query.from_user.id
    ] = target

    await query.message.reply_text(

f"""✅ Reply mode ON

🎯 Target User:

`{target}`

📨 Send text/photo now.

Use /cancel_reply to stop.
""",

        parse_mode="Markdown"

    )


# ---------- AUTO REPLY ----------

def auto_reply(text):

    t = text.lower()

    if "proxy" in t:

        return """🤖 Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network"""

    bn_words = [
        "কি",
        "vai",
        "ভাই",
        "দাদা",
        "problem",
        "help"
    ]

    if any(
        x in t
        for x in bn_words
    ):

        return "📝 সমস্যাটা বিস্তারিত বলুন"

    return "📝 Please explain clearly."


# ---------- HANDLE ----------

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    text = update.message.text or ""

    # ===== ADMIN REPLY MODE =====

    if user.id == ADMIN_ID:

        if user.id in reply_mode:

            target = reply_mode[user.id]

            try:

                if update.message.photo:

                    photo = update.message.photo[-1].file_id

                    await context.bot.send_photo(

                        chat_id=target,

                        photo=photo,

                        caption=update.message.caption

                    )

                    await update.message.reply_text(
                        "✅ Photo Sent"
                    )

                    return

                if update.message.text:

                    await context.bot.send_message(

                        chat_id=target,

                        text=update.message.text

                    )

                    await update.message.reply_text(
                        "✅ Reply Sent"
                    )

                    return

            except Exception as e:

                await update.message.reply_text(

f"""❌ Send Failed

{e}
"""
                )

                return

    # ===== USER SIDE =====

    bot_reply = auto_reply(text)

    await update.message.reply_text(
        bot_reply
    )

    keyboard = InlineKeyboardMarkup(

        [[

            InlineKeyboardButton(

                "💬 Reply",

                callback_data=f"reply_{user.id}"

            )

        ]]
    )

    admin_text = f"""

👤 User:

{user.full_name}

🆔 ID:

`{user.id}`

📩 Message:

{text}

🤖 Bot Reply:

{bot_reply}

"""

    await context.bot.send_message(

        chat_id=ADMIN_ID,

        text=admin_text,

        parse_mode="Markdown",

        reply_markup=keyboard

    )


# ---------- MAIN ----------

def main():

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

            filters.TEXT |
            filters.PHOTO,

            handle

        )

    )

    print("Bot Running...")

    app.run_polling()


if __name__ == "__main__":

    main()
