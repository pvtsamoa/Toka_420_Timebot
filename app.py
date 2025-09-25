from __future__ import annotations
import os, logging
from pathlib import Path as _Path
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Env / Logging ------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing in environment (.env)")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)

from services.news_fetcher import fetch_headlines

# --- Helpers ------------------------------------------------------------------
NEWS_DIR = _Path("data/news")

def _trim(text: str, limit: int = 180) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"

def _pick_news(region: str, limit: int = 180) -> str:
    try:
        f = NEWS_DIR / f"{region.lower()}.txt"
        if not f.exists():
            return f"[no pool for {region}]"
        lines = [
            ln.strip()
            for ln in f.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        if not lines:
            return f"[pool empty: {region}]"
        import random as _rnd
        return _trim(_rnd.choice(lines), limit)
    except Exception as e:
        return f"[error: {type(e).__name__}]"

# --- Handlers -----------------------------------------------------------------
async def status(update, context: ContextTypes.DEFAULT_TYPE):
    from services.runtime import get_x_state
    from datetime import datetime, timezone

    # Helper: find next job by predicate
    def _next_job(jobs, pred):
        js = [j for j in jobs if getattr(j, "next_run_time", None) and pred(j)]
        return min(js, key=lambda j: j.next_run_time) if js else None

    # Pull all jobs once
    try:
        jobs = context.application.job_queue.jobs() or []
    except Exception:
        jobs = []

    # (1) Next 4:20
    j_420 = _next_job(jobs, lambda j: str(getattr(j, "name", "")).startswith("420_"))
    if j_420:
        hub_420 = j_420.name.replace("420_", "")
        when_420 = j_420.next_run_time.strftime("%Y-%m-%d %H:%M UTC")
        line_420 = f"Next 4:20 → {hub_420} at {when_420}"
    else:
        line_420 = "Next 4:20 → (not scheduled)"

    # (2) Last X relay attempt
    xs = get_x_state()
    last_when = xs.get("last_attempt_iso") or "never"
    last_status = xs.get("last_status", "unknown")
    last_error = xs.get("last_error", "")
    if last_status == "ok":
        line_x_last = f"X relay (last): ✅ ok at {last_when}"
    elif last_status == "error":
        line_x_last = f"X relay (last): ⚠️ error at {last_when}" + (f" — {last_error}" if last_error else "")
    else:
        line_x_last = "X relay (last): ⭕ no record"

    # (3) Next scheduled X relay
    name_lc = lambda j: str(getattr(j, "name", "")).lower()
    j_x = _next_job(
        jobs,
        lambda j: any(k in name_lc(j) for k in ("x_relay", "tweet", "post_to_x", "x-Relay", "x:"))
    )
    if j_x:
        when_x = j_x.next_run_time.strftime("%Y-%m-%d %H:%M UTC")
        line_x_next = f"X relay (next): 🗓️ {getattr(j_x, 'name', 'job')} at {when_x}"
    elif j_420:
        when_x = j_420.next_run_time.strftime("%Y-%m-%d %H:%M UTC")
        line_x_next = f"X relay (next): 🗓️ assumed at next 4:20 ({when_x})"
    else:
        line_x_next = "X relay (next): (not scheduled)"

    text = (
        "✅ Toka is breathing. Schedules armed. 🌿\n"
        + line_420 + "\n"
        + line_x_last + "\n"
        + line_x_next
    )
    await update.message.reply_text(text)

async def _preroll_fire(context):
    chat_id = context.job.data
    await context.bot.send_message(chat_id=chat_id, text="🔥 Pre-roll: test 4:20 ritual fired.")

async def preroll(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    when = 60  # seconds
    context.job_queue.run_once(_preroll_fire, when, data=chat_id, name="preroll_test")
    await update.message.reply_text("🕒 Pre-roll armed — will fire in ~60s.")

async def news(update, context: ContextTypes.DEFAULT_TYPE):
    # 1) Live headlines (crypto + cannabis)
    sources_env = os.getenv("NEWS_SOURCES")  # comma URLs; defaults resolved in fetcher
    live = []
    try:
        live = fetch_headlines(sources_env, max_items=6)
    except Exception:
        live = []

    if live:
        lines = [f"• {t} — {src}\n{u}" for (t, u, src) in live]
        msg = "🗞️ Crypto & Cannabis headlines\n" + "\n\n".join(lines)
        if len(msg) > 3500:
            msg = msg[:3499]
        await update.message.reply_text(msg)
        return

    # 2) Fallback to local pools by region names
    regions_env = os.getenv("NEWS_REGIONS", "Samoa,California,London")
    regions = context.args or [r.strip() for r in regions_env.split(",") if r.strip()]
    regions = regions[:6]
    try:
        NEWS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    bits = [f"• {r}: {_pick_news(r)}" for r in regions]
    msg = "🗞️ Headlines\n" + "\n".join(bits)
    if len(msg) > 3500:
        msg = msg[:3499]
    await update.message.reply_text(msg)

# --- Optional scheduler hook (safe if missing) --------------------------------
try:
    from scheduler import schedule_hubs  # your hub scheduler
except Exception:
    schedule_hubs = None

try:
    from services.ritual_time import ritual_call  # job fired at each 4:20
except Exception:
    ritual_call = None

# --- Build Application & wire handlers ----------------------------------------
def build_app() -> Application:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers (idempotent)
    existing = {
        h.command[0] for h in application.handlers.get(0, [])
        if hasattr(h, "command") and h.command
    }
    if "status" not in existing:
        application.add_handler(CommandHandler("status", status))
    if "preroll" not in existing:
        application.add_handler(CommandHandler("preroll", preroll))
    if "news" not in existing:
        application.add_handler(CommandHandler("news", news))

    # Schedule 4:20 jobs if the modules are available
    if schedule_hubs and ritual_call:
        schedule_hubs(application.job_queue, ritual_call)

    return application

# --- Entrypoint ----------------------------------------------------------------
if __name__ == "__main__":
    app = build_app()
    app.run_polling()
