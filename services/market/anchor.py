import os, time
from typing import Optional, Dict, Tuple
from services.rituals.types import MarketAnchor
from .dexscreener import fetch_anchor

_TTL = int(os.getenv("TOKA_MARKET_TTL", "90"))  # seconds
_CACHE: Dict[str, Tuple[float, Optional[float], Optional[float], Optional[float]]] = {}
# key -> (ts, price, change, vol)

def _env_float(key: str) -> Optional[float]:
    v = os.getenv(key)
    try:
        return float(v) if v is not None else None
    except ValueError:
        return None

def _from_env(symbol: str) -> MarketAnchor:
    return MarketAnchor(
        symbol=symbol.upper(),
        price=_env_float("TOKA_SMOKE_PRICE"),
        change_24h_pct=_env_float("TOKA_SMOKE_CHANGE_PCT"),
        volume_24h=_env_float("TOKA_SMOKE_VOL_24H"),
    )

def get_market_anchor(symbol: str) -> MarketAnchor:
    """
    Live-first via Dexscreener with a short TTL cache.
    Falls back to env 'smoke' values if network/data is missing.
    """
    key = symbol.upper()

    # Cache hit?
    now = time.time()
    hit = _CACHE.get(key)
    if hit and (now - hit[0]) < _TTL:
        _, p, c, v = hit
        return MarketAnchor(symbol=key, price=p, change_24h_pct=c, volume_24h=v)

    # Try live fetch
    p, c, v = fetch_anchor(key)
    if p is not None and c is not None and v is not None:
        _CACHE[key] = (now, p, c, v)
        return MarketAnchor(symbol=key, price=p, change_24h_pct=c, volume_24h=v)

    # Fallback to env
    return _from_env(key)
