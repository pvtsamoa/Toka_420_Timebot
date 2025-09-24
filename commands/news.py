import xml.etree.ElementTree as ET, requests
from telegram import Update
from telegram.ext import ContextTypes
from config import SETTINGS

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

# Fallback “global” rotation if TELEGRAM_SCOPE=all or unknown
GLOBAL_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

def _pick_feeds(arg_scope: str | None) -> list[str]:
    # CLI override wins (e.g., /news apac)
    if arg_scope and arg_scope.lower() in FEEDS_BY_SCOPE:
        return FEEDS_BY_SCOPE[arg_scope.lower()]
    # .env scope (apac|emea|amer)
    env_scope = (SETTINGS.TELEGRAM_SCOPE or "").lower()
    if env_scope in FEEDS_BY_SCOPE:
        return FEEDS_BY_SCOPE[env_scope]
    return GLOBAL_FEEDS

def _fetch_one(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        chan_title = (root.findtext("./channel/title") or "").strip()
        item = root.find("./channel/item")
        if item is None:
            return None
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            return None
        return chan_title, title, link
    except Exception:
        return None

async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # optional region override: /news apac|emea|amer
    override = (context.args[0].strip().lower() if context.args else None)
    feeds = _pick_feeds(override)

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
            await update.message.reply_text("\n".join(lines))
            return

    await update.message.reply_text("ℹ️ No fresh headlines right now.")
