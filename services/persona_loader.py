import os, json, random
from functools import lru_cache
from config import SETTINGS

def _slug(name: str) -> str:
    return name.lower().replace(" ", "")

@lru_cache(maxsize=64)
def load_persona(hub_name: str) -> dict:
    """Load media/personas/<hub>.json. Returns {} if missing/invalid."""
    pdir = os.path.join(SETTINGS.MEDIA_DIR, "personas")
    path = os.path.join(pdir, f"{_slug(hub_name)}.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                j = json.load(f)
                if isinstance(j, dict):
                    return j
    except Exception:
        pass
    return {}

def choose(persona: dict, key: str, fallback_list: list[str] | None = None) -> str:
    items = persona.get(key) if isinstance(persona.get(key), list) else []
    if items:
        return random.choice([str(x) for x in items if str(x).strip()]) or ""
    if fallback_list:
        return random.choice([str(x) for x in fallback_list if str(x).strip()]) or ""
    return ""
