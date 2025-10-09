import os
from typing import Dict, Tuple, Callable
from telegram.ext import Application, CommandHandler

# map: command -> (module, attr)
_COMMANDS: Dict[str, Tuple[str, str]] = {
    "status": ("commands.status", "status"),
    "token":  ("commands.token", "token"),
    "news":   ("commands.news", "news"),
    "x_relay":("commands.x_relay", "x_relay"),  # hidden
    "chatid": ("commands.chatid", "chatid"),    # hidden
    "admin":  ("commands.admin", "admin"),      # consolidated admin
}

def _safe_import(mod: str, attr: str) -> Callable:
    try:
        m = __import__(mod, fromlist=[attr])
        return getattr(m, attr)
    except Exception:
        return None

def register_enabled_commands(app: Application) -> None:
    raw = os.getenv("TOKA_ENABLED_COMMANDS", "").strip()
    if not raw:
        return
    enabled = [c.strip().lstrip("/").lower() for c in raw.split(",") if c.strip()]
    for cmd in enabled:
        spec = _COMMANDS.get(cmd)
        if not spec:
            continue
        fn = _safe_import(*spec)
        if not fn:
            continue
        app.add_handler(CommandHandler(cmd, fn))
