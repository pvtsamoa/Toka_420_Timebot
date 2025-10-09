from __future__ import annotations
import time
from typing import List, Dict, Any

def _age_str(ts: float)->str:
    delta = max(0, time.time() - ts)
    h = int(delta//3600); m = int((delta%3600)//60)
    return f"{h}h {m}m ago" if h else f"{m}m ago"

def _pick_emoji(title:str)->str:
    t = title.lower()
    if any(k in t for k in ("weed","cannabis","hemp","420","thc","cbd")):
        return "🌿"
    if any(k in t for k in ("bitcoin","btc")):
        return "₿"
    if any(k in t for k in ("ethereum","eth")):
        return "♦️"
    if any(k in t for k in ("stablecoin","usdt","usdc")):
        return "🪙"
    return "🗞️"

def render_news(items: List[Dict[str,Any]])->str:
    if not items:
        return "🗞️ No fresh headlines right now. Try again soon."
    lines = []
    for it in items:
        emoji = _pick_emoji(it["title"])
        lines.append(f"{emoji} {it['title']} — {it.get('source','') or ''} ({_age_str(it['ts'])})\n{it['url']}")
    return "📰 *Toka News Wire*\n" + "\n\n".join(lines)
