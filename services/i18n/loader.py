import os, yaml, threading
from functools import lru_cache
from typing import Optional

_LANG = os.getenv("TOKA_LANG", "sm").lower()  # global default (kept for fallback)
_BASE = "services/rituals/i18n"
_LOCK = threading.Lock()

def _safe_read(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

@lru_cache(maxsize=8)
def _load_lang(lang: str) -> dict:
    lang = (lang or "sm").lower()
    path = f"{_BASE}/{lang}.yml"
    return _safe_read(path)

def set_lang(lang: str) -> None:
    global _LANG
    with _LOCK:
        _LANG = (lang or "sm").lower()
        _load_lang.cache_clear()

def get_lang() -> str:
    return _LANG

def t(key: str, default: str = "", lang: Optional[str] = None) -> str:
    """
    Dot-path lookup, e.g., 'labels.pre_roll'
    Optional lang override for per-chat rendering.
    """
    data = _load_lang((lang or _LANG).lower())
    node = data
    for seg in key.split("."):
        if not isinstance(node, dict):
            return default
        node = node.get(seg)
    return node if isinstance(node, str) else default
