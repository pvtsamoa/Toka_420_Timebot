import os, random, json
from services.dexscreener import get_anchor
DEFAULT_TOKEN = os.getenv("DEFAULT_TOKEN", "WEED")
def _pick(lst, default=""): 
    try: return random.choice(lst) if lst else default
    except: return default
def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
def load_media_bank():
    base = os.path.join(os.path.dirname(__file__), "..", "media")
    return {
        "jokes": _load_json(os.path.join(base, "jokes.json")) or [],
        "safety": _load_json(os.path.join(base, "safety.json")) or [],
        "proverbs": _load_json(os.path.join(base, "proverbs.json")) or [],
    }
MEDIA = load_media_bank()
def kiss_anchor(token_id: str):
    data = get_anchor(token_id or DEFAULT_TOKEN)
    if not data: return f"{token_id or DEFAULT_TOKEN}: price n/a, vol n/a, 24h ±0.00%"
    return f"{data['symbol']}: {data['change24']} | {data['price']} | 24h vol {data['vol24']}"
def build_ritual_text(hub_name: str, token_id: str = None):
    anchor = kiss_anchor(token_id or DEFAULT_TOKEN)
    proverb = _pick(MEDIA.get("proverbs", []), "")
    shield = _pick(MEDIA.get("safety", []), "DYOR • Stay balanced • Obey local laws")
    lines = [f"🌊 Toka 4:20 — {hub_name}", f"📈 {anchor}", f"🛡 {shield}"]
    if proverb: lines.append(f"🌺 {proverb}")
    return "\n".join(lines)
