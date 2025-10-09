from __future__ import annotations

# Keep lines tight; X limit ~280 chars (we cut at 274 upstream)
TAGS = "#Weedcoin #420Community #CryptoPositive"

def preroll_line(symbol: str, price: str) -> str:
    # Short dawn mood; no emojis to keep room
    return f"Preroll 4:00 — {symbol} {price}. Patience is mana; conviction the compass. {TAGS}"

def holy_minute_line(symbol: str, price: str, change_pct: str) -> str:
    return f"4:20 Holy Minute — {symbol} {price} ({change_pct}). We rise together; roots deep, flame pure. {TAGS}"

def anchor_line(kiss_line: str) -> str:
    # Use the already-rendered compact KISS line from your service
    return f"{kiss_line} {TAGS}"

def news_digest_line(hub: str) -> str:
    # Title only; headlines stay in Telegram — X is just the beacon.
    h = hub.title()
    return f"Toka’s 4:20 {h} digest just dropped on Telegram. Sail in peace. {TAGS}"
