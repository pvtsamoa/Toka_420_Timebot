import xml.etree.ElementTree as ET
import requests
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import SETTINGS

logger = logging.getLogger(__name__)

# News category sources - reliable feeds only
CRYPTO_NEWS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://bitcoinmagazine.com/feed/rss",
    "https://cryptoslate.com/feed/",
]

MARKET_NEWS = [
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.reuters.com/reuters/businessNews",
]

# Regional fallback feeds
REGIONAL_FEEDS = {
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

# Track user call counts for rotation
_user_calls = {}


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


def _get_category_cycle(user_id: int) -> str:
    """Rotate through 2 categories per user call (crypto → markets)."""
    global _user_calls
    
    call_count = _user_calls.get(user_id, 0)
    category_idx = call_count % 2
    
    _user_calls[user_id] = call_count + 1
    
    categories = ["crypto", "market"]
    return categories[category_idx]


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send rotating news: cannabis studies → cannabis news → crypto cannabis news."""
    user_id = update.effective_user.id
    logger.info(f"News command requested (user: {user_id})")
    
    try:
        # Get rotation category for this user
        category = _get_category_cycle(user_id)
        
        # Select feeds based on category
        if category == "crypto":
            feeds = CRYPTO_NEWS
            emoji = "💰"
            title = "Cryptocurrency News"
        else:  # market
            feeds = MARKET_NEWS
            emoji = "📈"
            title = "Market & Finance News"
        
        # Try each feed until we get an article
        result = None
        for url in feeds:
            result = _fetch_one(url)
            if result:
                logger.debug(f"✅ Got article from {url}")
                break
        
        # Fallback to regional feeds if all failed
        if not result:
            logger.debug("All category feeds failed, trying regional fallback")
            scope = (SETTINGS.TELEGRAM_SCOPE or "all").lower()
            fallback_feeds = REGIONAL_FEEDS.get(scope, [])
            for url in fallback_feeds:
                result = _fetch_one(url)
                if result:
                    logger.debug(f"✅ Got article from fallback feed")
                    break
        
        if not result:
            await update.message.reply_text(
                f"⚠️ Could not fetch {title.lower()} right now.\n\n"
                f"Try again in a few moments.",
                parse_mode="Markdown"
            )
            logger.warning(f"Could not fetch any news for category {category}")
            return
        
        chan_title, article_title, link = result
        
        message = f"""
{emoji} **{title}**

**{article_title}**

📰 Source: {chan_title}
🔗 [Read more]({link})

────────────────────
*Call `/news` again for the next category*
*Categories rotate: Crypto → Markets*
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ Sent {category} news to user {user_id}: {article_title[:50]}")
        
    except Exception as e:
        logger.exception(f"Error in news command: {e}")
        await update.message.reply_text(
            "⚠️ Error fetching news. Try again later.",
            parse_mode="Markdown"
        )
