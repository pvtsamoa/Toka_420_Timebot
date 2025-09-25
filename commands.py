from __future__ import annotations
from typing import Callable, Awaitable, Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

def _optional_import(path: str, name: str) -> Optional[Callable[..., Awaitable[None]]]:
    try:
        mod = __import__(path, fromlist=[name])
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    except Exception:
        pass
    return None

async def _not_installed(label: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"⚠️ /{label} not installed in this build.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("✅ Toka is breathing. Schedules armed. 🌿")

_news     = _optional_import("commands.news", "news")
_token    = _optional_import("commands.token", "token")
_preroll  = _optional_import("commands.preroll", "preroll")
_space    = _optional_import("commands.space", "space")
_x        = _optional_import("commands.x", "x")
_id       = _optional_import("commands.user_id", "user_id") or _optional_import("commands.id", "id")

_COMMANDS: list[tuple[str, Callable[..., Awaitable[None]]]] = [
    ("status",  status),
    ("news",    _news    or (lambda u,c: _not_installed("news", u, c))),
    ("token",   _token   or (lambda u,c: _not_installed("token", u, c))),
    ("preroll", _preroll or (lambda u,c: _not_installed("preroll", u, c))),
    ("space",   _space   or (lambda u,c: _not_installed("space", u, c))),
    ("x",       _x       or (lambda u,c: _not_installed("x", u, c))),
    ("id",      _id      or (lambda u,c: _not_installed("id", u, c))),
]

def add_handlers(application: Application) -> None:
    existing = {
        h.command[0] for h in application.handlers.get(0, [])
        if isinstance(h, CommandHandler) and h.command
    }
    for cmd, fn in _COMMANDS:
        if cmd not in existing:
            application.add_handler(CommandHandler(cmd, fn))
