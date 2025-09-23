import xml.etree.ElementTree as ET, requests
from telegram import Update
from telegram.ext import ContextTypes
RSS = [
  "https://www.coindesk.com/arc/outboundfeeds/rss/",
  "https://cointelegraph.com/rss",
  "https://decrypt.co/feed",
]
def _fetch_one(url: str):
    try:
        r = requests.get(url, timeout=10); root = ET.fromstring(r.content)
        for item in root.findall(".//item")[:5]:
            t = (item.findtext("title") or "").strip()
            if t: return t
    except Exception: return None
async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for u in RSS:
        t = _fetch_one(u)
        if t: await update.message.reply_text(f"📰 {t}"); return
    await update.message.reply_text("ℹ️ No news found right now.")
