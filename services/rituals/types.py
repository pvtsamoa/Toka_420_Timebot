from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class RitualKey(str, Enum):
    PRE_ROLL = "pre_roll"
    HOLY_MINUTE = "holy_minute"

@dataclass
class MarketAnchor:
    symbol: str                   # e.g., "WEED", "BTC"
    price: Optional[float]        # last price
    change_24h_pct: Optional[float]
    volume_24h: Optional[float]   # KISS: just these 3 + price

@dataclass
class HubInfo:
    name: str                     # e.g., "Los Angeles"
    tz: str                       # IANA tz, e.g., "America/Los_Angeles"

@dataclass
class RitualContext:
    hub: HubInfo
    ritual_dt_iso: str            # ISO timestamp at hub TZ
    chat_token: str               # per-chat token selection
    market: MarketAnchor
    moon_phase: Optional[str] = None
    extra: Dict[str, Any] = None
