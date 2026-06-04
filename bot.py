import os
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
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

ADMIN_ID = 5196850561

reply_mode = {}

# ---------------- START ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Hello! Send your problem."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

"""📌 Commands

/start
/help
/cancel_reply
"""
    )


async def cancel_reply(update: Update, context):

    if update.effective_user.id != ADMIN_ID:
        return

    reply_mode.pop(
        ADMIN_ID,
        None
    )

    await update.message.reply_text(
        "❌ Reply mode OFF"
    )


# ---------------- REPLY BUTTON ----------------

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

🎯 Target:

`{target}`

Send text/photo now.

Use /cancel_reply
""",

        parse_mode="Markdown"

    )


# ---------------- AUTO REPLY ----------------

def auto_reply(text):

    t = text.lower()

    if "proxy" in t:

        return """🤖 Proxy issue?

1. Restart network
2. Rotate IP
3. Check expiry
4. Try another network"""

    bangla_words = [

        "ভাই",
        "কি",
        "সমস্যা",
        "দাদা",
        "vai"

    ]

    if any(
        x in text.lower()
        for x in bangla_words
    ):

        return "📝 সমস্যাটা বিস্তারিত বলুন"

    return "📝 Please explain clearly."


# ---------------- HANDLE ----------------

async def handle(update: Update, context):

    user = update.effective_user

    text = update.message.text or ""

    # ---------- ADMIN REPLY MODE ----------

    if user.id == ADMIN_ID:

        if ADMIN_ID in reply_mode:

            target = reply_mode[
                ADMIN_ID
            ]

            try:

                if update.message.photo:

                    await context.bot.send_photo(

                        chat_id=target,

                        photo=update.message.photo[-1].file_id,

                        caption=update.message.caption

                    )

                    await update.message.reply_text(
                        "✅ Photo Sent"
                    )

                    return

                if update.message.text:

                    await context.bot.send_message(

                        chat_id=target,

                        text=text

                    )

                    await update.message.reply_text(
                        "✅ Reply Sent"
                    )

                    return

            except Exception as e:

                await update.message.reply_text(

f"""❌ Failed

{e}
"""
                )

                return

    # ---------- USER SIDE ----------

    bot_reply = auto_reply(
        text
    )

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

    admin_message = f"""

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

        text=admin_message,

        parse_mode="Markdown",

        reply_markup=keyboard

    )


# ---------------- MAIN ----------------

async def main():

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

    print(
        "Bot Running..."
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
