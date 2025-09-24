import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from scheduler import schedule_hubs
from services.ritual_time import ritual_call
from commands.status import status
from commands.token import token
def build_app():
    load_dotenv(override=True)
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("token", token))
    schedule_hubs(app.job_queue, ritual_call)
    return app
if __name__ == "__main__":
    build_app().run_polling(drop_pending_updates=True)
