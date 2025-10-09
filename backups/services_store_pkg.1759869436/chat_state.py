import json, os, threading
from typing import Dict

_STATE_PATH = os.getenv("TOKA_STATE_FILE", "data/chat_state.json")
_DEFAULT_TOKEN = os.getenv("TOKA_DEFAULT_TOKEN", "WEEDCOIN")
_DEFAULT_LANG = os.getenv("TOKA_DEFAULT_LANG", "sm")  # 'sm' Samoan-first
_DEFAULT_SHOW_MOON = False
_LOCK = threading.Lock()

def _ensure_dirs():
    os.makedirs(os.path.dirname(_STATE_PATH), exist_ok=True)

def _load() -> Dict:
    _ensure_dirs()
    if not os.path.exists(_STATE_PATH):
        return {"tokens": {}, "lang": {}, "moon": {}}
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("tokens", {})
            data.setdefault("lang", {})
            data.setdefault("moon", {})
            return data
    except Exception:
        return {"tokens": {}, "lang": {}, "moon": {}}

def _save(state: Dict) -> None:
    _ensure_dirs()
    tmp = _STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _STATE_PATH)

# --- token ---
def set_chat_token(chat_id: int, token: str) -> None:
    with _LOCK:
        st = _load()
        st.setdefault("tokens", {})[str(chat_id)] = token.upper()
        _save(st)

def get_chat_token(chat_id: int) -> str:
    with _LOCK:
        st = _load()
        tok = st.get("tokens", {}).get(str(chat_id))
        return tok if tok else _DEFAULT_TOKEN

def get_default_token() -> str:
    return _DEFAULT_TOKEN

# --- lang ---
def set_chat_lang(chat_id: int, lang: str) -> None:
    lang = lang.lower()
    if lang not in ("sm", "en"):
        lang = _DEFAULT_LANG
    with _LOCK:
        st = _load()
        st.setdefault("lang", {})[str(chat_id)] = lang
        _save(st)

def get_chat_lang(chat_id: int) -> str:
    with _LOCK:
        st = _load()
        return st.get("lang", {}).get(str(chat_id), _DEFAULT_LANG)

# --- moon toggle ---
def set_chat_show_moon(chat_id: int, on: bool) -> None:
    with _LOCK:
        st = _load()
        st.setdefault("moon", {})[str(chat_id)] = bool(on)
        _save(st)

def get_chat_show_moon(chat_id: int) -> bool:
    with _LOCK:
        st = _load()
        val = st.get("moon", {}).get(str(chat_id))
        return bool(val) if val is not None else _DEFAULT_SHOW_MOON


# --- global target chat id (used for admin fallback) ---
def get_global_target_chat(default: int = 0) -> int:
    with _LOCK:
        st = _load()
        try:
            v = int(st.get("global_target_chat_id", default))
        except Exception:
            v = default
        return v
