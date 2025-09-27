import requests, xml.etree.ElementTree as ET
from typing import List, Tuple, Dict
from services.log import get_logger

logger = get_logger()

SOURCES: Dict[str, str] = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "Marijuana Moment": "https://www.marijuanamoment.net/feed/",
    "High Times": "https://hightimes.com/feed/",
}

CANNABIS_KW = {"cannabis","weed","marijuana","hemp","420"}
CRYPTO_KW   = {"crypto","bitcoin","btc","ethereum","eth","token","coin","defi","nft","blockchain","web3","solana","sol"}

def _parse_rss(xml_bytes: bytes) -> List[Tuple[str, str, str]]:
    out = []
    try:
        root = ET.fromstring(xml_bytes)
        for it in root.findall(".//item"):
            title = (it.findtext("title") or "").strip()
            link  = (it.findtext("link") or "").strip()
            desc  = (it.findtext("description") or "").strip()
            if title and link:
                out.append((title, link, desc))
    except Exception as e:
        logger.warning("RSS parse error: %s", e)
    return out

def _matches_cannabis_crypto(title: str, desc: str) -> bool:
    text = f"{title} {desc}".lower()
    return any(k in text for k in CANNABIS_KW) and any(k in text for k in CRYPTO_KW)

def fetch_canna_crypto(max_per_source: int = 2) -> Dict[str, List[Tuple[str,str]]]:
    results = {}
    for name, url in SOURCES.items():
        items = []
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            for t, link, d in _parse_rss(r.content):
                if _matches_cannabis_crypto(t, d):
                    items.append((t, link))
                if len(items) >= max_per_source:
                    break
        except Exception as e:
            logger.warning("Fetch failed for %s: %s", name, e)
        results[name] = items
    return results
