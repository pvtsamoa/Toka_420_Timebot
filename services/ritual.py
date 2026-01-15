import os
import random
import json
import logging
from services.dexscreener import get_anchor

logger = logging.getLogger(__name__)

DEFAULT_TOKEN = os.getenv("DEFAULT_TOKEN", "WEED")

def _pick(lst, default=""):
    """Safely pick a random item from a list."""
    try:
        return random.choice(lst) if lst else default
    except Exception as e:
        logger.warning(f"Error picking from list: {e}")
        return default

def _load_json(path):
    """Safely load JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Loaded JSON from {path}")
            return data
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error loading JSON from {path}: {e}")
        return []

def load_media_bank():
    """Load all media files (jokes, safety tips, proverbs)."""
    base = os.path.join(os.path.dirname(__file__), "..", "media")
    try:
        media = {
            "jokes": _load_json(os.path.join(base, "jokes.json")) or [],
            "safety": _load_json(os.path.join(base, "safety.json")) or [],
            "proverbs": _load_json(os.path.join(base, "proverbs.json")) or [],
        }
        logger.debug(f"Loaded media bank: {len(media['jokes'])} jokes, {len(media['safety'])} safety tips, {len(media['proverbs'])} proverbs")
        return media
    except Exception as e:
        logger.exception(f"Failed to load media bank: {e}")
        return {"jokes": [], "safety": [], "proverbs": []}

MEDIA = load_media_bank()

def kiss_anchor(token_id: str):
    """Get formatted price anchor for a token."""
    try:
        data = get_anchor(token_id or DEFAULT_TOKEN)
        if not data:
            logger.debug(f"No price data for {token_id or DEFAULT_TOKEN}")
            return f"{token_id or DEFAULT_TOKEN}: price n/a, vol n/a, 24h ±0.00%"
        return f"{data['symbol']}: {data['change24']} | {data['price']} | 24h vol {data['vol24']}"
    except Exception as e:
        logger.exception(f"Error getting anchor for {token_id}: {e}")
        return f"{token_id or DEFAULT_TOKEN}: price n/a, vol n/a, 24h ±0.00%"

def build_ritual_text(hub_name: str, token_id: str = None):
    """Build the formatted ritual message for a hub."""
    try:
        anchor = kiss_anchor(token_id or DEFAULT_TOKEN)
        proverb = _pick(MEDIA.get("proverbs", []), "")
        shield = _pick(MEDIA.get("safety", []), "DYOR • Stay balanced • Obey local laws")
        
        lines = [f"🌊 Toka 4:20 — {hub_name}", f"📈 {anchor}", f"🛡 {shield}"]
        if proverb:
            lines.append(f"🌺 {proverb}")
        
        return "\n".join(lines)
    except Exception as e:
        logger.exception(f"Error building ritual text for {hub_name}: {e}")
        return f"🌊 Toka 4:20 — {hub_name}\n⚠️ Error generating ritual text. Please retry."
