import json, os, random, logging

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _load(name: str, key: str) -> list[str]:
    path = os.path.join(BASE, f"{name}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        arr = obj.get(key, [])
        return [s.strip() for s in arr if isinstance(s, str) and s.strip()]
    except Exception as e:
        logging.warning("Pool load error %s: %s", name, e)
        return []

_EDU = _load("education", "education")
_SAF = _load("safety", "safety")

def pick_edu() -> str | None:
    return random.choice(_EDU) if _EDU else None

def pick_safety() -> str | None:
    return random.choice(_SAF) if _SAF else None

def pick_combo() -> tuple[str|None, str|None]:
    # Alternate light: mostly edu, sometimes safety
    if random.random() < 0.5:
        return (pick_edu(), None)
    return (None, pick_safety())
