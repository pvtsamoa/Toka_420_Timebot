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
    """Load all media files (quotes, safety tips, tokens)."""
    base = os.path.join(os.path.dirname(__file__), "..", "media")
    try:
        media = {
            "quotes": _load_json(os.path.join(base, "cannabis_quotes.json")) or [],
            "safety": _load_json(os.path.join(base, "safety.json")) or [],
            "tokens": _load_json(os.path.join(base, "cannabis_tokens.json")) or [],
        }
        logger.debug(f"Loaded media bank: {len(media['quotes'])} quotes, {len(media['safety'])} safety tips, {len(media['tokens'])} tokens")
        return media
    except Exception as e:
        logger.exception(f"Failed to load media bank: {e}")
        return {"quotes": [], "safety": [], "tokens": []}

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
    """Build the formatted ritual message for a hub.
    
    Format: Blessing → Token → Safety → Quote
    """
    try:
        # Get blessing, token, safety tip, and quote
        from services.navigator_blessing import get_blessing
        
        blessing = get_blessing()
        token = _pick(MEDIA.get("tokens", []), {"symbol": "WEED", "name": "Weedcoin"})
        safety = _pick(MEDIA.get("safety", []), "DYOR • Use 2FA • Secure your keys")
        quote_obj = _pick(MEDIA.get("quotes", []), {})
        quote = f'"{quote_obj.get("quote", "Stay blessed")}" — {quote_obj.get("source", "Cannabis Culture")}' if quote_obj else ""
        
        # Get price anchor for featured token
        anchor = kiss_anchor(token.get("symbol", "WEED").lower())
        
        lines = [
            f"🌿⛵️ SPARK IT UP — 4:20 in {hub_name}!",
            "",
            "✨ Navigator's Blessing",
            blessing,
            "",
            f"💰 Featured Token: {token.get('name', 'Cannabis')}",
            anchor,
            "",
            "🛡️ Crypto Safety",
            safety,
        ]
        
        if quote:
            lines.append("")
            lines.append("🎬 Cannabis Culture")
            lines.append(quote)
        
        lines.append("")
        lines.append("Spark responsibly. HODL wise. 🌲")
        
        return "\n".join(lines)
    except Exception as e:
        logger.exception(f"Error building ritual text for {hub_name}: {e}")
        return f"🌿⛵️ SPARK IT UP — 4:20 in {hub_name}!\n⚠️ Error generating ritual. Please retry."
