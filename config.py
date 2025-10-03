import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

def _req(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env: {name}")
    return v

# --- Required ---
TELEGRAM_BOT_TOKEN = _req("TELEGRAM_BOT_TOKEN")
SUA_CHAT_ID        = _req("SUA_CHAT_ID")  # e.g., -100...

# --- X / Twitter (optional; feature flag true only if all present) ---
X_CONSUMER_KEY    = os.getenv("X_CONSUMER_KEY")
X_CONSUMER_SECRET = os.getenv("X_CONSUMER_SECRET")
X_ACCESS_TOKEN    = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET   = os.getenv("X_ACCESS_SECRET")
HAS_X = all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET])

# --- Optional (AI) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# --- Defaults ---
DEFAULT_TOKEN = os.getenv("DEFAULT_TOKEN", "WEEDCOIN")
FALLBACK_CHAT = os.getenv("FALLBACK_CHAT", "SUA")
