# commands/status.py — Navigator Log style
import os, datetime as dt
from services.ritual import kiss_anchor

def _fmt_delta(delta: dt.timedelta) -> str:
    secs = int(delta.total_seconds())
    if secs < 0: secs = 0
    h, r = divmod(secs, 3600); m, _ = divmod(r, 60)
    return f"{h}h {m}m"

def _next_ritual(context):
    # Find the soonest scheduled 4:20 across hubs
    jobs = context.application.job_queue.jobs()
    next_times = [j.next_t for j in jobs if j and j.name and j.name.startswith("420_") and j.next_t]
    if not next_times:
        return None, None
    nxt = min(next_times)
    hub = [j.name.replace("420_", "") for j in jobs if j.next_t == nxt][0]
    return hub, nxt

async def status(update, context):
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "WEED")
    anchor = kiss_anchor(token)

    # Scheduler snapshot
    hub, nxt = _next_ritual(context)
    now = dt.datetime.now(dt.timezone.utc)
    nxt_txt = f"{nxt:%H:%M} UTC (in {_fmt_delta(nxt - now)})" if nxt else "—"

    # Compose Navigator Log
    lines = []
    lines.append("🌿⛵️ Navigator Log — Toka v4")
    lines.append("—" * 34)
    lines.append("🕰 Scheduler")
    lines.append(f"🟢 Next ritual:  {nxt_txt} — {hub if hub else ''}")
    lines.append("• Last ritual:  —")
    lines.append("")
    lines.append("📊 Anchor:")
    lines.append(f"  {anchor}")
    lines.append("📚 Education: 🟢")
    lines.append("🛡 Safety: 🟢")
    lines.append("")
    lines.append("✨🌺 Navigator’s Blessing ✨")
    lines.append("🌿")
    lines.append("")
    lines.append("📈 Bongterm > FOMO — zoom out before you wig out.")
    await update.message.reply_text("\n".join(lines))
