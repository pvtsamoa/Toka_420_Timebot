from __future__ import annotations
import os, time, math, re
from typing import List, Dict, Any
import feedparser

# ----------- Sources -----------
# Global baseline (always included as fallback)
DEFAULT_SOURCES = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
    "https://www.benzinga.com/feeds/rss/markets/cryptocurrency",
    "https://mjbizdaily.com/feed/",
    "https://cryptoslate.com/feed/",
]

# Regional hubs (add/adjust freely; we keep reliable RSS-capable sources)
HUB_SOURCES = {
    # JP/SEA blend
    "asia": [
        "https://coinpost.jp/?feed=rss2",         # CoinPost (JP)
        "https://coincu.com/feed/",               # Coincu (SEA-heavy)
        "https://finbold.com/feed/",              # Finbold (often APAC-timed)
    ],
    # UK/EU blend
    "europe": [
        "https://www.cityam.com/topic/cryptocurrency/feed/",
        "https://cryptoslate.com/feed/",
        "https://www.benzinga.com/feeds/rss/markets/cryptocurrency",
    ],
    # US-focused
    "americas": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
        "https://www.benzinga.com/feeds/rss/markets/cryptocurrency",
        "https://mjbizdaily.com/feed/",
    ],
    # AU/NZ/Samoa (Oceania)
    "oceania": [
        "https://www.afr.com/markets/rss",        # AFR markets (crypto-adjacent)
        "https://cryptoslate.com/feed/",          # global with AU/NZ timing overlap
        "https://www.benzinga.com/feeds/rss/markets/cryptocurrency",
    ],
}

# Weedcoin & cannabis-crypto priority
KEYWORDS_WEEDCOIN = [
    r"\bweedcoin\b", r"\bweed coin\b", r"\b\$WEED\b", r"\b WEED\b"
]
KEYWORDS_CANNABIS = [
    r"\bcannabis\b", r"\bweed\b", r"\b420\b", r"\bhemp\b", r"\bTHC\b", r"\bCBD\b",
]
KEYWORDS_MAJORS = [
    r"\bBTC\b", r"\bBitcoin\b", r"\bETH\b", r"\bEthereum\b",
    r"\bUSDT\b", r"\bUSDC\b", r"\bSOL\b"
]
KEYWORDS_CRYPTO = [
    r"\bcrypto\b", r"\bblockchain\b", r"\bDeFi\b", r"\bWeb3\b", r"\bexchange\b", r"\btoken\b"
]

# Light regional hints (for Germany, UK, Thailand, Australia, New Zealand, Japan, Samoa)
KEYWORDS_REGIONAL = {
    "europe": [r"\bGermany\b", r"\bGerman\b", r"\bUK\b", r"\bBritain\b", r"\bLondon\b", r"\bEU\b", r"\bEurope\b"],
    "asia": [r"\bJapan\b", r"\bTokyo\b", r"\bThailand\b", r"\bBangkok\b", r"\bSingapore\b"],
    "oceania": [r"\bAustralia\b", r"\bAussie\b", r"\bNew Zealand\b", r"\bNZ\b", r"\bSamoa\b"],
    "americas": [r"\bUS\b", r"\bUSA\b", r"\bNew York\b", r"\bLA\b", r"\bCanada\b"],
}

def _now_ts()->float: return time.time()

def _score_base(title:str, summary:str)->float:
    text = f"{title} {summary}".lower()
    score = 0.0
    # Weedcoin gets the highest bump
    for pat in KEYWORDS_WEEDCOIN:
        if re.search(pat, text, flags=re.I): score += 8.0
    # Cannabis-crypto first
    for pat in KEYWORDS_CANNABIS:
        if re.search(pat, text, flags=re.I): score += 4.0
    # Majors & general crypto
    for pat in KEYWORDS_MAJORS:
        if re.search(pat, text, flags=re.I): score += 2.0
    for pat in KEYWORDS_CRYPTO:
        if re.search(pat, text, flags=re.I): score += 1.0
    # small readability preference
    score += max(0.0, 2.0 - len(title)/140.0)
    return score

def _age_penalty(published_ts: float)->float:
    # half-life ~ 24h
    hours = max(0.0, (_now_ts() - published_ts) / 3600.0)
    return math.exp(-hours / 24.0)

def _norm_item(e)->Dict[str,Any]:
    title = e.get("title","").strip()
    link = e.get("link","").strip()
    summ = (e.get("summary") or e.get("description") or "").strip()
    # published
    ts = _now_ts()
    if e.get("published_parsed"): ts = time.mktime(e["published_parsed"])
    elif e.get("updated_parsed"): ts = time.mktime(e["updated_parsed"])
    return {
        "title": title,
        "url": link,
        "summary": summ,
        "ts": float(ts),
        "source": (e.get("source",{}) or {}).get("title") or e.get("author") or "",
    }

def _dedupe(items: List[Dict[str,Any]])->List[Dict[str,Any]]:
    seen = set(); out=[]
    for it in items:
        key = (it["title"].lower(), it["url"])
        if key in seen: continue
        seen.add(key); out.append(it)
    return out

def _load_feed(url:str)->List[Dict[str,Any]]:
    try:
        d = feedparser.parse(url)
        return [_norm_item(e) for e in (d.entries or [])]
    except Exception:
        return []

def _sources_for(hub:str)->List[str]:
    hub = (hub or "").lower().strip()
    # env override: comma-separated list
    env_src = [s.strip() for s in (os.environ.get("NEWS_SOURCES","") or "").split(",") if s.strip()]
    if env_src: return env_src
    srcs = list(DEFAULT_SOURCES)
    if hub in HUB_SOURCES:
        # put hub sources first
        srcs = HUB_SOURCES[hub] + [s for s in srcs if s not in HUB_SOURCES[hub]]
    return srcs

def fetch_news(limit:int=5, lane:str="all", hub:str="americas")->List[Dict[str,Any]]:
    """
    lane: 'all' | 'cannabis' | 'majors'
    hub:  'asia' | 'europe' | 'americas' | 'oceania'
    """
    sources = _sources_for(hub)
    items: List[Dict[str,Any]] = []
    for src in sources:
        items.extend(_load_feed(src))

    if not items:
        return []

    # score + recency + hub hint
    for it in items:
        base = _score_base(it["title"], it["summary"])
        # lane emphasis
        if lane == "cannabis":
            base *= 1.25
        elif lane == "majors":
            base *= 1.1
        # regional hint (soft)
        for pat in KEYWORDS_REGIONAL.get(hub, []):
            if re.search(pat, f"{it['title']} {it['summary']}", flags=re.I):
                base *= 1.08
                break
        it["score"] = base * _age_penalty(it["ts"])

    items = sorted(_dedupe(items), key=lambda x: x.get("score",0.0), reverse=True)
    return items[:max(1, min(20, int(limit)))]
