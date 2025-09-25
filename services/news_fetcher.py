from __future__ import annotations
from typing import List, Tuple
import re
import feedparser

DEFAULT_SOURCES = [
    # Crypto
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    # Cannabis (policy/business that could move markets)
    "https://www.marijuanamoment.net/feed/",
    "https://mjbizdaily.com/feed/",
]

_CRYPTO   = {"crypto","cryptocurrency","bitcoin","ethereum","btc","eth","web3","defi","token","blockchain","stablecoin","etf"}
_CANNABIS = {"cannabis","marijuana","weed","hemp","thc","cbd","dispensary","reschedule","deschedule","legalization","regulation"}

def _normalize_sources(sources_env: str | None) -> List[str]:
    if not sources_env:
        return DEFAULT_SOURCES
    return [p.strip() for p in sources_env.split(",") if p.strip()]

def _clean(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip())

def fetch_headlines(sources_env: str | None, max_items: int = 6) -> List[Tuple[str, str, str]]:
    """
    Returns up to max_items of (title, url, source_name), filtered to crypto/cannabis topics.
    """
    sources = _normalize_sources(sources_env)
    seen: set[tuple[str, str]] = set()
    out: List[Tuple[str, str, str]] = []

    for url in sources:
        try:
            feed = feedparser.parse(url)
            src_name = _clean(feed.feed.get("title", "") or url)
            for e in feed.entries[:20]:
                title = _clean(e.get("title", ""))
                link  = (e.get("link") or "").strip()
                if not title or not link:
                    continue
                key = (title, link)
                if key in seen:
                    continue
                seen.add(key)

                blob = f"{title} {e.get('summary','')}"
                blob_low = blob.lower()
                is_crypto = any(k in blob_low for k in _CRYPTO)
                is_canna  = any(k in blob_low for k in _CANNABIS)
                if not (is_crypto or is_canna):
                    continue

                out.append((title, link, src_name))
                if len(out) >= max_items:
                    return out
        except Exception:
            # Skip a broken feed and continue
            continue

    return out
