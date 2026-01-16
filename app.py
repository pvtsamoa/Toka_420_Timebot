import os
import sys
import logging
from dotenv import load_dotenv
from telegram import BotCommand
from telegram.ext import Application, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.config_validator import validate_config
from services.error_handler import on_error
from scheduler import schedule_hubs
from services.ritual_time import ritual_call

from commands.start import start
from commands.status import status
from commands.news import news
from commands.token import token, health_check


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

logger = logging.getLogger("toka.app")


def configure_logging() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(LOG_DIR, "bot.log"), encoding="utf-8"),
        ],
        encoding="utf-8",
    )


async def set_bot_info(app: Application) -> None:
    try:
        await app.bot.set_my_description(
            "Cannabis culture + cryptocurrency price alerts. Daily 4:20 rituals with blessing, tokens, safety tips & quotes."
        )
        await app.bot.set_my_commands(
            [
                BotCommand("start", "View command guide & bot info"),
                BotCommand("status", "Bot health check & blessing"),
                BotCommand("token", "Token price (default: weedcoin)"),
                BotCommand("news", "Cryptocurrency & market news rotation"),
                BotCommand("health", "Quick health status"),
            ]
        )
        logger.info("Bot info updated successfully")
    except Exception as e:
        logger.warning("Could not update bot info: %s", e)


def build_app() -> Application:
    logger.info("Building Toka 420 Time Bot...")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    # Windows-safe: avoid PTB JobQueue weakref crash
    app = (
        Application.builder()
        .token(bot_token)
        .job_queue(None)
        .build()
    )

    # Error handler
    app.add_error_handler(on_error)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("token", token))
    app.add_handler(CommandHandler("health", health_check))

    # Start APScheduler and schedule hubs (04:20 in each hub timezone)
    sched = AsyncIOScheduler(timezone=os.getenv("TZ", "America/Los_Angeles"))
    sched.start()

    schedule_hubs(sched, ritual_call, app=app)
    logger.info("Scheduler armed (APScheduler): %d jobs", len(sched.get_jobs()))

    # Keep reference alive
    app.bot_data["apscheduler"] = sched

    # Clean shutdown for APScheduler
    async def _shutdown_scheduler(app: Application) -> None:
        sched = app.bot_data.get("apscheduler")
        if sched:
            logger.info("Shutting down APScheduler...")
            sched.shutdown(wait=False)

    app.post_shutdown = _shutdown_scheduler

    # Telegram UI metadata (runs once after init)
    app.post_init = set_bot_info

    logger.info("Bot initialized successfully")
    return app


def main() -> int:
    configure_logging()

    logger.info("=" * 60)
    logger.info("Toka 420 Time Bot v1 Starting")
    logger.info("=" * 60)

    load_dotenv(override=True)
    logger.info("Environment loaded from .env")

    validate_config()

    app = build_app()

    logger.info("Starting polling...")
    app.run_polling(drop_pending_updates=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        logger.exception("Fatal error during startup: %s", e)
        raise SystemExit(1)
