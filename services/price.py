import time, requests, logging
from typing import Optional, Tuple
from services.storage import KV
from config import SETTINGS
log = logging.getLogger("price")
CACHE_TTL = 60
_last = {"ts": 0, "q": None, "data": None}
DEX_URL = "https://api.dexscreener.com/latest/dex/search?q={query}"
def get_anchor(query: str) -> Optional[Tuple[float,float,float]]:
    now = time.time()
    if query == _last["q"] and now - _last["ts"] < CACHE_TTL and _last["data"]:
        return _last["data"]
    try:
        r = requests.get(DEX_URL.format(query=query), timeout=10); j = r.json()
        first = (j.get("pairs") or [{}])[0]
        price = float(first.get("priceUsd", 0.0))
        pct = float((first.get("priceChange") or {}).get("h24", 0.0))
        vol = float((first.get("volume") or {}).get("h24", 0.0))
        data = (price, pct, vol)
        _last.update(ts=now, q=query, data=data)
        KV.log({"t": now, "q": query, "price": price, "pct": pct, "vol": vol})
        return data
    except Exception as e:
        log.warning("dex error: %s", e); return None
def default_query(chat_id: int) -> str:
    return SETTINGS.WEEDCOIN_TOKEN or "Weedcoin"
