from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_SCOPE: str = os.getenv("TELEGRAM_SCOPE", "all")
    FF_NEWS: bool = os.getenv("FF_NEWS", "1") == "1"
    FF_X_RELAY: bool = os.getenv("FF_X_RELAY", "0") == "1"
    FF_PRE_ROLL: bool = os.getenv("FF_PRE_ROLL", "1") == "1"

    CHAT_IDS: str = os.getenv("CHAT_IDS", "")
    WEEDCOIN_TOKEN: str = os.getenv("WEEDCOIN_TOKEN", "Weedcoin")

    BASE_DIR: str = os.getcwd()
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    MEDIA_DIR: str = os.path.join(BASE_DIR, "media")

SETTINGS = Settings()
