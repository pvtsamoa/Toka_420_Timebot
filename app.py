import os
import logging
import signal
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from services.config_validator import validate_config
from services.error_handler import on_error
from scheduler import schedule_hubs
from services.ritual_time import ritual_call
from commands.status import status
from commands.news import news
from commands.studies import studies
from commands.token import token, health_check

# Configure logging
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

app = None

def build_app():
    """Build and configure the Telegram bot application."""
    logger.info("Building Toka 420 Time Bot...")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    app = Application.builder().token(bot_token).build()
    
    # Add error handler
    app.add_error_handler(on_error)
    
    # Register command handlers
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("studies", studies))
    app.add_handler(CommandHandler("token", token))
    app.add_handler(CommandHandler("health", health_check))
    
    # Schedule recurring rituals
    logger.info("Scheduling hub rituals...")
    if app.job_queue:
        schedule_hubs(app.job_queue, ritual_call)
    
    logger.info("✅ Bot initialized successfully")
    return app

async def shutdown_handler(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT."""
    global app
    logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    
    if app:
        if app.job_queue:
            logger.info("Stopping job queue...")
            app.job_queue.stop()
        logger.info("Stopping application...")
        await app.stop()
    
    logger.info("✅ Shutdown complete")
    sys.exit(0)

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("🌿⛵ Toka 420 Time Bot v1 Starting")
        logger.info("=" * 60)
        
        # Load environment
        load_dotenv(override=True)
        logger.info("✅ Environment loaded from .env")
        
        # Validate configuration
        validate_config()
        
        # Build bot
        app = build_app()
        
        # Register shutdown handlers
        signal.signal(signal.SIGTERM, lambda s, f: __import__('asyncio').run(shutdown_handler(s, f)))
        signal.signal(signal.SIGINT, lambda s, f: __import__('asyncio').run(shutdown_handler(s, f)))
        logger.info("✅ Shutdown handlers registered")
        
        # Start polling
        logger.info("🚀 Starting polling...")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.exception(f"💥 Fatal error during startup: {e}")
        sys.exit(1)
