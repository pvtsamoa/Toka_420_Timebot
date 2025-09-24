import os, json, random, time
from typing import List, Tuple
from services.storage import KV
from config import SETTINGS

PACK_ORDER = ["proverbs", "jokes", "safety", "market"]

def _load_bank(name: str) -> List[str]:
    path = os.path.join(SETTINGS.MEDIA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        return []

def rotate_blessing() -> Tuple[str, str]:
    """Rotate through pack types; pick a random line within the chosen pack."""
    state = KV.get()
    idx = int(state.get("blunt_idx", 0))
    pack = PACK_ORDER[idx % len(PACK_ORDER)]
    items = _load_bank(pack)
    text = random.choice(items) if items else f"(missing {pack}.json)"
    state["blunt_idx"] = idx + 1
    KV.set(state)
    return pack, text

def packs_health() -> Tuple[bool, bool]:
    """Return (education_ok, safety_ok) based on media packs being present."""
    edu_ok = bool(_load_bank("proverbs") or _load_bank("market"))
    safety_ok = bool(_load_bank("safety"))
    return edu_ok, safety_ok
