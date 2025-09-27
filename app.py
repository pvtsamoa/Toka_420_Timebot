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
    chat_id = os.getenv("TELEGRAM_DEV_CHAT_ID")  # group/channel/user id
    if not bot_token or not chat_id:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_DEV_CHAT_ID")
    app = Application.builder().token(bot_token).build()
    app.add_error_handler(on_error)
    schedule_hubs(app.job_queue, int(chat_id))
    return app

if __name__ == "__main__":
    build_app().run_polling(allowed_updates=None, stop_signals=None)
