import logging
from telegram.ext import Application, CommandHandler
from config import SETTINGS
from core.registry import REGISTRY
log = logging.getLogger("tg")
class TelegramAdapter:
    def __init__(self):
        if not SETTINGS.TELEGRAM_TOKEN:
            log.warning("TELEGRAM_TOKEN missing — telegram adapter disabled")
            self.app = None
        else:
            self.app = Application.builder().token(SETTINGS.TELEGRAM_TOKEN).build()
            REGISTRY.register("telegram", "4.0")
    def add_handler(self, command: str, fn):
        if self.app: self.app.add_handler(CommandHandler(command, fn))
    async def send(self, chat_id: int, text: str):
        if self.app: await self.app.bot.send_message(chat_id, text)
    def run_polling(self):
        if self.app: self.app.run_polling()
        else: log.warning("telegram not started (no token)")
