import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def get_logger() -> logging.Logger:
    log_dir = Path("logs"); log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("toka420")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_dir / "bot.log", maxBytes=512_000, backupCount=1)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger
