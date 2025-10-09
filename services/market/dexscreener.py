import os, time, logging
from typing import Optional, Dict, Any, Tuple, List
import requests

log = logging.getLogger(__name__)

DEX_TIMEOUT = float(os.getenv("TOKA_DEX_TIMEOUT", "6.0"))

def _search(symbol_or_addr: str) -> Optional[Dict[str, Any]]:
    """
    Calls Dexscreener search endpoint.
    Returns the top 'pair' dict or None.
    """
    q = symbol_or_addr.strip()
    url = f"https://api.dexscreener.com/latest/dex/search?q={q}"
    try:
        r = requests.get(url, timeout=DEX_TIMEOUT)
        if r.status_code != 200:
            log.warning("Dexscreener non-200: %s", r.status_code)
            return None
        data = r.json()
    except Exception as e:
        log.warning("Dexscreener error: %s", e)
        return None

    pairs: List[Dict[str, Any]] = data.get("pairs") or []
    if not pairs:
        return None

    # Prefer pairs that actually match symbol exactly, else take first
    sym = q.upper()
    best = None
    for p in pairs:
        base_sym = (p.get("baseToken") or {}).get("symbol") or ""
        if base_sym.upper() == sym:
            best = p
            break
    if best is None:
        best = pairs[0]
    return best

def fetch_anchor(symbol_or_addr: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Returns (price_usd, change_pct_24h, vol_24h_usd) or (None, None, None).
    """
    pair = _search(symbol_or_addr)
    if not pair:
        return (None, None, None)

    # Dexscreener pair fields
    # priceUsd: str/float, volume.h24: number, priceChange.h24: number
    price_raw = pair.get("priceUsd")
    vol = None
    change = None

    volume_block = pair.get("volume") or {}
    vol = volume_block.get("h24")
    change_block = pair.get("priceChange") or {}
    change = change_block.get("h24")

    def _to_float(v):
        try:
            return float(v)
        except Exception:
            return None

    price = _to_float(price_raw)
    vol = _to_float(vol)
    change = _to_float(change)
    return (price, change, vol)
