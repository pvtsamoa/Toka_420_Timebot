import logging
from telegram.error import NetworkError

async def on_error(update, context):
    # Quietly swallow intermittent network blips from long-polling
    if isinstance(context.error, NetworkError):
        logging.warning("Network glitch during polling: %s", context.error)
        return
    # Log anything else normally
    logging.exception("Unhandled error: %s", context.error)
