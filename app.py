import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from services.error_handler import on_error
from scheduler.jobs import schedule_hubs
from services.log import get_logger

logger = get_logger()

def build_app():
    load_dotenv(override=True)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_DEV_CHAT_ID")  # group/channel/user id (can be negative)
    if not bot_token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_DEV_CHAT_ID")

    app = Application.builder().token(bot_token).build()

    # error handler
    app.add_error_handler(on_error)

    # ——— register ONLY the intended commands ———
    from commands.status import status
    from commands.token import token
    from commands.news import news
    from commands.x import x
    from commands.chatid import chatid

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("token",  token))
    app.add_handler(CommandHandler("news",   news))
    app.add_handler(CommandHandler("x",      x))
    app.add_handler(CommandHandler("chatid", chatid))  # hidden

    # schedule preroll/holy jobs to TELEGRAM_DEV_CHAT_ID
    schedule_hubs(app.job_queue, int(chat_id))

    return app

if __name__ == "__main__":
    build_app().run_polling(allowed_updates=None, stop_signals=None)
