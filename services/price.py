import time, requests
from typing import Dict
from services.log import get_logger
from config import PRICE_TTL_SEC

logger = get_logger()
_cache = {"ts": 0.0, "token": None, "data": None}

def _fmt_usd(x):
    try:
        v = float(x)
    except Exception:
        return str(x)
    if v >= 1_000_000_000:
        return f"B"
    if v >= 1_000_000:
        return f"M"
    if v >= 1_000:
        return f"k"
    return f"" if v < 1 else f""

def get_anchor(token: str) -> Dict[str, str]:
    now = time.time()
    if _cache["token"] == token and now - _cache["ts"] < PRICE_TTL_SEC and _cache["data"]:
        return _cache["data"]

    url = f"https://api.dexscreener.com/latest/dex/search?q={token}"
    price = "n/a"; ch24 = "n/a"; vol24 = "n/a"; mcap = "n/a"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        j = r.json()
        pair = (j.get("pairs") or [None])[0]
        if pair:
            price = _fmt_usd(pair.get("priceUsd") or pair.get("price", "n/a"))
            # 24h change
            ch24v = (pair.get("priceChange") or {}).get("h24")
            ch24 = f"{float(ch24v):+,.2f}%" if ch24v not in (None, "") else "n/a"
            # 24h volume
            vol24v = (pair.get("volume") or {}).get("h24") or pair.get("volume24h")
            vol24 = _fmt_usd(vol24v) if vol24v not in (None, "") else "n/a"
            # market cap (prefer marketCap, else fdv)
            mcap_raw = pair.get("marketCap") or pair.get("fdv")
            mcap = _fmt_usd(mcap_raw) if mcap_raw not in (None, "") else "n/a"
    except Exception as e:
        logger.warning("Price fetch failed: %s", e)

    data = {"price": price, "change_24h": ch24, "volume_24h": vol24, "market_cap": mcap}
    _cache.update({"ts": now, "token": token, "data": data})
    return data
