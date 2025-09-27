from typing import Dict, List, Tuple

# Stoner terms (metrics/objects)
STONER = {
    "price": "Nug",
    "change_24h": "Buzz (24h)",
    "volume_24h": "Smoke cloud (Vol)",
    "market_cap": "Stash (Cap)",
}

# Navigator phrasing (movement/timing)
NAV = {
    "preroll": "roll up",   # 4:00
    "holy": "light up",     # 4:20
    "last": "Last blunt",
    "next": "Next blunt",
    "relay_on": "Paddle: IN",
    "relay_off": "Paddle: OUT",
    "tide_report": "Toka Navigator’s Tide Report",
}

def _val(x):
    return str(x) if (x is not None and x != "") else "n/a"

def status_text(last_holy: str, next_summary: str, x_on: bool) -> str:
    last_line = f"{NAV[last]}: {last_holy}"
    next_line = f"{NAV[next]}: {next_summary}"
    pad_line  = NAV["relay_on"] if x_on else NAV["relay_off"]
    return (
        f"✅ {NAV[tide_report]}\n"
        f"🌊 {last_line}\n"
        f"🌅 {next_line}\n"
        f"🚣 {pad_line}"
    )

def token_text(token: str, anchor: Dict[str, str]) -> str:
    p   = _val(anchor.get("price"))
    ch  = _val(anchor.get("change_24h"))
    vol = _val(anchor.get("volume_24h"))
    cap = _val(anchor.get("market_cap"))
    return (
        f"💱 {token.upper()}\n"
        f"{STONER[price]}: {p}\n"
        f"{STONER[change_24h]}: {ch}\n"
        f"{STONER[volume_24h]}: {vol}\n"
        f"{STONER[market_cap]}: {cap}"
    )

def preroll_text(hub: str) -> str:
    return (
        f"🌊 Talofa navigator — {NAV[preroll]} @ 4:00 — {hub}\n"
        f"Set the sail: check liquidity, glance at depth, line up your anchors."
    )

def holy_text(hub: str, token: str, anchor: Dict[str, str]) -> str:
    p   = _val(anchor.get("price"))
    ch  = _val(anchor.get("change_24h"))
    vol = _val(anchor.get("volume_24h"))
    cap = _val(anchor.get("market_cap"))
    return (
        f"🌊 Talofa navigator — {NAV[holy]} @ 4:20 — {hub}\n"
        f"💱 {token.upper()}\n"
        f"{STONER[price]}: {p} | {STONER[change_24h]}: {ch} | "
        f"{STONER[volume_24h]}: {vol} | {STONER[market_cap]}: {cap}\n"
        f"🌺 Blessing: Ua tafe le vasa, ae tumau le ma‘anunu — the tide moves, but the anchor holds."
    )

def news_text(results: Dict[str, List[Tuple[str, str]]]) -> str:
    lines: List[str] = ["🗞️ Crypto news — talanoa of the tides"]
    added = 0
    for source, items in results.items():
        if not items:
            continue
        lines.append(f"- {source}:")
        for title, link in items:
            lines.append(f"  • {title}\n    {link}")
            added += 1
    if added == 0:
        lines.append("(no relevant headlines right now)")
    return "\n".join(lines)
