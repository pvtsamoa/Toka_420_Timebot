from telegram.ext import ContextTypes
from services.log import get_logger
logger = get_logger()

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error: %s", context.error)
