from typing import Dict

def preroll_text(hub: str) -> str:
    return f"⏳ Pre-roll @ 4:00 — {hub}\nPrepare charts, check liquidity, line up your anchors."

def holy_text(hub: str, token: str, anchor: Dict[str, str]) -> str:
    return (
        f"🕰️ Holy Minute 4:20 — {hub}\n"
        f"{token}: {anchor['price']} | 24h {anchor['change_24h']} | 24h vol {anchor['volume_24h']}"
    )
