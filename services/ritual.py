from datetime import datetime
import pytz, requests, xml.etree.ElementTree as ET

from config import SETTINGS
from services.price import get_anchor
from services.persona import toka_anchor_line
from services.runtime import rotate_blessing, _load_bank  # _load_bank is safe to reuse
from services.persona_loader import load_persona, choose

DEFAULT_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]

def _fetch_headline(feeds: list[str]) -> tuple[str, str] | None:
    for u in feeds:
        try:
            r = requests.get(u, timeout=10)
            r.raise_for_status()
            root = ET.fromstring(r.content)
            chan = (root.findtext("./channel/title") or "").strip()
            item = root.find("./channel/item")
            if item is None: 
                continue
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link")  or "").strip()
            if title and link:
                return (f"{chan}" if chan else "Crypto News", link if link.startswith("http") else "")
        except Exception:
            continue
    return None

def compose_preroll(hub: dict, symbol: str) -> str:
    # simple vibe-setter
    hub_name = hub.get("name", "Unknown Hub")
    return f"⛵️ Pre-roll @ 4:00 — {hub_name}\nSetting sail for 4:20 | token: {symbol or SETTINGS.WEEDCOIN_TOKEN}"

def compose_ritual(hub: dict, symbol: str) -> str:
    hub_name = hub.get("name", "Unknown Hub")
    persona = load_persona(hub_name)

    # greeting / blessing
    greeting = choose(persona, "greetings")
    blessing_pack, blessing = rotate_blessing()  # global rotation (proverb/joke/safety/market)
    blessing_line = blessing

    # safety (persona safety -> fallback global safety.json)
    safety_pool = _load_bank("safety")
    safety_line = choose(persona, "safety", safety_pool)

    # anchor
    q = symbol or SETTINGS.WEEDCOIN_TOKEN
    anchor = get_anchor(q)
    anchor_text = toka_anchor_line(q, anchor) if anchor else f"⚠️ Anchor unavailable for {q}. Keep calm, paddle on."

    # news: prefer persona feeds, fallback to defaults
    feeds = persona.get("news_feeds") or DEFAULT_FEEDS
    hl = _fetch_headline(feeds)
    news_text = f"📰 {hl[0]}\n🔗 {hl[1]}" if hl else "📰 No fresh headline."

    # meme (persona memes -> fallback jokes.json)
    meme_pool = _load_bank("jokes")
    meme = choose(persona, "memes", meme_pool)

    # time tag
    now = datetime.now(tz=pytz.timezone(hub.get("tz", "UTC"))).strftime("%H:%M %Z")

    lines = []
    lines.append(f"🌿✨ Holy Minute — {hub_name} 4:20 ✨🌿")
    if greeting: lines.append(f"\n{greeting}")
    lines.append(f"\n{anchor_text}")
    if safety_line: lines.append(f"\n🛡️ {safety_line}")
    lines.append(f"\n{news_text}")
    if meme: lines.append(f"\n🔥 {meme}")
    lines.append(f"\n⏱ {now} | fa‘asamoa: Bongterm > FOMO.")
    return "\n".join(lines)
