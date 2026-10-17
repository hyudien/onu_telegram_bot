import os

from settings import load_dotenv

load_dotenv()

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from handlers.start import (
    start,
    access_callback
)

from handlers.register import (
    menu_handler,
    callback_handler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN belum diatur. Isi file .env terlebih dahulu.")

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            access_callback,
            pattern="^(acc_|reject_)"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT &
            ~filters.COMMAND,
            menu_handler
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
