# app.py
from dotenv import load_dotenv

from config import SETTINGS
from core.logging import setup_logging
from adapters.telegram_bot import TelegramAdapter

# commands
from commands.status import status_cmd
from commands.id import id_cmd
from commands.token import token_cmd
from commands.news import news_cmd

# scheduler
from scheduler.setup import register_jobs


def main() -> None:
    """Boot the bot, attach handlers, and start polling (blocking)."""
    load_dotenv()
    log = setup_logging()

    tg = TelegramAdapter()

    # If TELEGRAM_TOKEN is missing, adapter exposes app=None
    if not getattr(tg, "app", None):
        log.warning("Add TELEGRAM_TOKEN to .env then run again.")
        print("Toka 420 TimeBot v4: Telegram disabled (no token).")
        return

    # Handlers
    tg.add_handler("status", status_cmd)
    tg.add_handler("id", id_cmd)
    tg.add_handler("token", token_cmd)
    tg.add_handler("news", news_cmd)

    # Scheduler (pre-roll & ritual across configured chats)
    try:
        register_jobs(tg.app)
    except Exception as exc:
        log.exception("Scheduler failed to initialize: %s", exc)

    print("Toka 420 TimeBot v4 — running")
    tg.run_polling()  # blocks; manages its own event loop (PTB v20+)


if __name__ == "__main__":
    main()
