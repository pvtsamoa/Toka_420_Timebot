import time, urllib.request, xml.etree.ElementTree as ET

# Simple per-hub feed map (can expand later per region/source)
FEEDS = {
    # crypto-focused global feeds (safe default for any hub)
    "DEFAULT": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://blockworks.co/rss",
        "https://decrypt.co/feed",
    ],
    # examples if you want hub-specific later; they currently fall back to DEFAULT
    "HONOLULU": [],
    "MEXICO CITY": [],
    "LOS ANGELES": [],
    "NEW YORK": [],
    "LONDON": [],
    "TOKYO": [],
}

_CACHE = {}  # {feed_url: (timestamp, [(title, source), ...])}
_TTL   = 1800  # 30 min

def _parse_rss(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Toka420/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    # Try RSS 2.0
    chan = root.find("channel")
    if chan is not None:
        items = []
        for item in chan.findall("item"):
            t = (item.findtext("title") or "").strip()
            if not t: continue
            items.append((t, _host(url)))
        return items
    # Atom
    items = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        t = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        if not t: continue
        items.append((t, _host(url)))
    return items

def _host(url: str) -> str:
    try:
        return urllib.request.urlparse(url).hostname or "news"
    except Exception:
        return "news"

def _get_feed(url: str):
    now = time.time()
    if url in _CACHE and now - _CACHE[url][0] < _TTL:
        return _CACHE[url][1]
    try:
        items = _parse_rss(url)
    except Exception:
        items = []
    _CACHE[url] = (now, items)
    return items

def get_headlines(hub_name: str, limit: int = 1):
    hub_key = (hub_name or "").strip().upper()
    urls = [u for u in FEEDS.get(hub_key, []) if u] or FEEDS["DEFAULT"]
    seen = []
    for u in urls:
        for t, src in _get_feed(u):
            if t not in seen:
                seen.append((t, src))
            if len(seen) >= limit:
                return seen
    return seen[:limit]

def get_news_text(hub_name: str) -> str | None:
    """Return a single-line bullet like: 📰 Headline — source"""
    items = get_headlines(hub_name, limit=1)
    if not items:
        return None
    title, src = items[0]
    # trim a bit for chat readability
    if len(title) > 140:
        title = title[:137].rstrip() + "…"
    host = src.replace("www.", "")
    return f"📰 {title} — {host}"
