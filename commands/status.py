from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timezone
from services.schedule_state import get_status
from config import DEFAULT_TOKEN
# optional imports guarded
try:
    from services.store.chat_state import get_chat_hub, get_chat_token
except Exception:
    def get_chat_hub(chat_id, default_hub="americas"): return default_hub
    def get_chat_token(chat_id): return DEFAULT_TOKEN

def _fmt_dt(iso: str | None) -> str:
    if not iso: return "—"
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # show relative-ish + HH:MM UTC
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return "—"

def _x_state() -> str:
    try:
        from services.x_state import is_on
        return "on" if is_on() else "off"
    except Exception:
        return "off"

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    hub = get_chat_hub(chat_id, default_hub="americas")
    token = get_chat_token(chat_id) or DEFAULT_TOKEN

    # schedule snapshots
    holy   = get_status("holy_minute")
    prerl  = get_status("preroll")
    dawn   = get_status("news_dawn")

    # compose
    parts = [
        "🧭 *Toka Status*",
        f"• Hub: `{hub}`   • X relay: *{_x_state()}*",
        f"• Token: `{token}`",
        "",
        "*4:20 Schedule*",
        f"— Preroll:   last {_fmt_dt(prerl['last_posted_utc'])} | next {_fmt_dt(prerl['next_run_utc'])}",
        f"— Holy:      last {_fmt_dt(holy['last_posted_utc'])}  | next {_fmt_dt(holy['next_run_utc'])}",
        "",
        "*News Digests*",
        f"— Dawn (Americas): last {_fmt_dt(dawn['last_posted_utc'])} | next {_fmt_dt(dawn['next_run_utc'])}",
        "",
        "Sail calm — roots before riches.",
    ]
    await update.message.reply_markdown("\n".join(parts))
