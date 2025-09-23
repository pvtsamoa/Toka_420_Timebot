import asyncio
from dotenv import load_dotenv
from core.logging import setup_logging
from adapters.telegram_bot import TelegramAdapter
from commands.status import status_cmd, id_cmd
from commands.token import token_cmd
from commands.news import news_cmd
log = setup_logging()
load_dotenv()
async def main():
    tg = TelegramAdapter()
    if not tg.app:
        log.warning("Add TELEGRAM_TOKEN to .env then run again.")
        print("Toka 420 TimeBot v4: Telegram disabled (no token)."); return
    tg.add_handler("status", status_cmd)
    tg.add_handler("id", id_cmd)
    tg.add_handler("token", token_cmd)
    tg.add_handler("news", news_cmd)
    tg.run_polling()
if __name__ == "__main__":
    asyncio.run(main())
