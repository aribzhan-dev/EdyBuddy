from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import start_handler, message_handler
from bot.config import BOT_TOKEN


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # app.add_handler(CommandHandler("start", start_handler))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    app.run_polling(stop_signals=None)
    app.run_polling()


if __name__ == "__main__":
    main()