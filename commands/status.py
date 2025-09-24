from datetime import datetime, timedelta, time as dtime
import pytz
from telegram import Update
from telegram.ext import ContextTypes

from services.storage import KV
from services.price import get_anchor, default_query
from services.runtime import rotate_blessing, packs_health

# Keep in sync with scheduler/setup.py
DEFAULT_TZ = "America/Los_Angeles"

def _fmt_human_delta(dt: datetime, now: datetime) -> str:
    diff = dt - now
    sign = "-" if diff.total_seconds() < 0 else "in "
    secs = abs(int(diff.total_seconds()))
    h, r = divmod(secs, 3600)
    m, _ = divmod(r, 60)
    if h and m:
        return f"{sign}{h}h {m}m".strip()
    if h:
        return f"{sign}{h}h".strip()
    return f"{sign}{m}m".strip()

def _next_at(now: datetime, hh: int, mm: int) -> datetime:
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=1)
    return target

def _fmt_ts(ts: float | None, tz) -> str:
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(ts, tz).strftime("%H:%M %b%d")
    except Exception:
        return "—"

def _light(ok: bool, degraded: bool = False) -> str:
    if ok and not degraded: return "🟢"
    if degraded: return "🟡"
    return "🔴"

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone(DEFAULT_TZ)
    now = datetime.now(tz)

    # Next times
    nxt_pr = _next_at(now, 4, 0)
    nxt_rt = _next_at(now, 4, 20)

    # Last times from state
    state = KV.get()
    last_pr = _fmt_ts(state.get("last_preroll"), tz)
    last_rt = _fmt_ts(state.get("last_ritual"), tz)

    # Anchor health (quick check using default token; cached in service)
    anchor_ok = bool(get_anchor(default_query(0)))
    edu_ok, safety_ok = packs_health()

    # Build message (no Markdown parse_mode needed)
    lines = []
    lines.append("🌿⛵ Navigator Log — Toka v4")
    lines.append("--------------------------------")
    lines.append("⏰ Scheduler")
    lines.append(f"   • Next pre-roll: {nxt_pr.strftime('%H:%M')} ({_fmt_human_delta(nxt_pr, now)}) — {_light(True)}")
    lines.append(f"   • Next ritual:  {nxt_rt.strftime('%H:%M')} ({_fmt_human_delta(nxt_rt, now)}) — {_light(True)}")
    lines.append(f"   • Last pre-roll: {last_pr}")
    lines.append(f"   • Last ritual:   {last_rt}")
    lines.append("")
    lines.append(f"📈 Anchor: {_light(anchor_ok)}")
    lines.append(f"📚 Education: {_light(edu_ok)}")
    lines.append(f"🛡️ Safety: {_light(safety_ok)}")
    lines.append("")
    lines.append("--------------------------------")

    # Blessing rotation
    pack, blessing = rotate_blessing()
    title = "Navigator’s Blessing"
    aura = {"proverbs":"🌊","jokes":"🔥","safety":"🛡️","market":"📈"}.get(pack, "✨")
    lines.append(f"✨🌿✨  {title}  ✨🌿✨")
    lines.append("")
    lines.append(f"{aura} {blessing}")

    await update.message.reply_text("\n".join(lines))
