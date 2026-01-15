import xml.etree.ElementTree as ET
import requests
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import SETTINGS

logger = logging.getLogger(__name__)

# Regional feed sets (curated, fast, reliable)
FEEDS_BY_SCOPE = {
    "apac": [
        "https://ambcrypto.com/feed/",
        "https://www.newsbtc.com/feed/",
        "https://cointelegraph.com/rss",
    ],
    "emea": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cryptonews.com/news/feed/",
        "https://coinjournal.net/news/feed/",
    ],
    "amer": [
        "https://decrypt.co/feed",
        "https://bitcoinmagazine.com/feed/rss",
        "https://cryptoslate.com/feed/",
    ],
}

# Fallback "global" rotation if TELEGRAM_SCOPE=all or unknown
GLOBAL_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

def _pick_feeds(arg_scope: str | None) -> list[str]:
    """Select appropriate feeds based on scope."""
    # CLI override wins (e.g., /news apac)
    if arg_scope and arg_scope.lower() in FEEDS_BY_SCOPE:
        logger.debug(f"Using {arg_scope} feeds from command override")
        return FEEDS_BY_SCOPE[arg_scope.lower()]
    # .env scope (apac|emea|amer)
    env_scope = (SETTINGS.TELEGRAM_SCOPE or "").lower()
    if env_scope in FEEDS_BY_SCOPE:
        logger.debug(f"Using {env_scope} feeds from config")
        return FEEDS_BY_SCOPE[env_scope]
    logger.debug("Using global feeds")
    return GLOBAL_FEEDS

def _fetch_one(url: str):
    """Fetch the first item from an RSS feed."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        chan_title = (root.findtext("./channel/title") or "").strip()
        item = root.find("./channel/item")
        if item is None:
            logger.debug(f"No items in feed: {url}")
            return None
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            logger.debug(f"Invalid item in feed: {url}")
            return None
        return chan_title, title, link
    except requests.Timeout:
        logger.warning(f"Timeout fetching feed: {url}")
        return None
    except requests.RequestException as e:
        logger.warning(f"Request error fetching feed {url}: {e}")
        return None
    except ET.ParseError as e:
        logger.warning(f"XML parse error in feed {url}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching feed {url}: {e}")
        return None

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send latest cannabis/crypto news."""
    user_id = update.effective_user.id
    
    # optional region override: /news apac|emea|amer
    override = None
    if context.args:
        override = context.args[0].strip().lower()
        
        # Validate scope argument
        valid_scopes = list(FEEDS_BY_SCOPE.keys()) + ["all"]
        if override not in valid_scopes:
            logger.info(f"Invalid scope requested: {override} (user: {user_id})")
            await update.message.reply_text(f"❌ Invalid scope. Use: {', '.join(valid_scopes)}")
            return
    
    feeds = _pick_feeds(override)
    logger.info(f"Fetching news (scope: {override or 'default'}, user: {user_id})")

    for u in feeds:
        hit = _fetch_one(u)
        if hit:
            source, title, link = hit
            lines = [
                "📰 Market Pulse",
                "────────────────",
                f"{source}" if source else "Crypto News",
                f"• {title}",
                f"🔗 {link}",
            ]
            logger.info(f"Sent news article from {source} (user: {user_id})")
            await update.message.reply_text("\n".join(lines))
            return

    logger.info(f"No fresh headlines available (user: {user_id})")
    await update.message.reply_text("ℹ️ No fresh headlines right now.")
