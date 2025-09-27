from typing import Dict, List, Tuple
from pathlib import Path
import json, random

# Stoner terms (metrics/objects)
STONER = {
    "price": "💨 Nug",
    "change_24h": "📊 Buzz (24h)",
    "volume_24h": "☁️ Smoke cloud (Vol)",
    "market_cap": "🪙 Stash (Cap)",
}

# Navigator phrasing (movement/timing)
NAV = {
    "preroll": "🌱 Roll up",       # 4:00
    "holy": "🔥 Light up",         # 4:20
    "last": "Last blunt",
    "next": "Next blunt",
    "relay_on": "🚣 Paddle: IN",
    "relay_off": "🚣 Paddle: OUT",
    "tide_report": "✅ Toka Navigator’s Tide Report",
}

# ---- lightweight media pickers (use existing media/*.json) ----
_MEDIA_CACHE = {}

def _load_items(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        j = json.loads(raw)
        # Accept either a list[str] or an object with an "items" list
        if isinstance(j, list):
            items = j
        elif isinstance(j, dict) and "items" in j and isinstance(j["items"], list):
            items = j["items"]
        else:
            # flatten any stringy values
            items = [v for v in j.values() if isinstance(v, str)]
        # keep only non-empty strings and strip
        return [s.strip() for s in items if isinstance(s, str) and s.strip()]
    except Exception:
        return []

def _pick(kind: str) -> str:
    # kind in {"blessing","tip","joke"}
    if kind in _MEDIA_CACHE and _MEDIA_CACHE[kind]:
        return random.choice(_MEDIA_CACHE[kind])
    base = Path("media")
    if kind == "blessing":
        paths = [base / "proverbs.json"]
    elif kind == "tip":
        # prefer market tips; fall back to safety
        paths = [base / "market.json", base / "safety.json"]
    else:
        paths = [base / "jokes.json"]
    items: List[str] = []
    for p in paths:
        items.extend(_load_items(p))
    _MEDIA_CACHE[kind] = items
    return random.choice(items) if items else ""

def _val(x):
    return str(x) if (x is not None and x != "") else "n/a"

def status_text(last_holy: str, next_summary: str, x_on: bool) -> str:
    last_line = f"{NAV[last]}: {last_holy}"
    next_line = f"{NAV[next]}: {next_summary}"
    pad_line  = NAV["relay_on"] if x_on else NAV["relay_off"]
    return (
        f"{NAV[tide_report]}
"
        f"🌊 {last_line}
"
        f"🌅 {next_line}
"
        f"{pad_line}"
    )

def token_text(token: str, anchor: Dict[str, str]) -> str:
    p   = _val(anchor.get("price"))
    ch  = _val(anchor.get("change_24h"))
    vol = _val(anchor.get("volume_24h"))
    cap = _val(anchor.get("market_cap"))
    return (
        f"𓆉 {token.upper()}
"
        f"{STONER[price]}: {p}
"
        f"{STONER[change_24h]}: {ch}
"
        f"{STONER[volume_24h]}: {vol}
"
        f"{STONER[market_cap]}: {cap}"
    )

def preroll_text(hub: str) -> str:
    tip = _pick("tip")
    tip_line = f"📚 Tip: {tip}" if tip else ""
    return "
".join([
        f"🌊 Talofa navigator — {NAV[preroll]} @ 4:00 — {hub}",
        "Set the sail: check liquidity, glance at depth, line up your anchors.",
        tip_line
    ]).rstrip()

def holy_text(hub: str, token: str, anchor: Dict[str, str]) -> str:
    p   = _val(anchor.get("price"))
    ch  = _val(anchor.get("change_24h"))
    vol = _val(anchor.get("volume_24h"))
    cap = _val(anchor.get("market_cap"))
    bless = _pick("blessing")
    tip   = _pick("tip")
    joke  = _pick("joke")
    lines = [
        f"🌊 Talofa navigator — {NAV[holy]} @ 4:20 — {hub}",
        f"𓆉 {token.upper()}",
        f"{STONER[price]}: {p} | {STONER[change_24h]}: {ch} | {STONER[volume_24h]}: {vol} | {STONER[market_cap]}: {cap}",
    ]
    if bless: lines.append(f"🌺 Blessing: {bless}")
    if tip:   lines.append(f"📚 Tip: {tip}")
    if joke:  lines.append(f"🤣 {joke}")
    return "
".join(lines)

def news_text(results: Dict[str, List[Tuple[str, str]]]) -> str:
    lines: List[str] = ["🗞️ Crypto news — talanoa of the tides"]
    added = 0
    for source, items in results.items():
        if not items:
            continue
        lines.append(f"- {source}:")
        for title, link in items:
            lines.append(f"  • {title}
    {link}")
            added += 1
    if added == 0:
        lines.append("(no relevant headlines right now)")
    return "
".join(lines)
