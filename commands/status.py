import os
import logging
import datetime as dt
from services.ritual import kiss_anchor
from services.navigator_blessing import get_blessing

logger = logging.getLogger(__name__)


def _fmt_delta(delta: dt.timedelta) -> str:
    """Format timedelta as human-readable string."""
    secs = int(delta.total_seconds())
    if secs < 0:
        secs = 0
    h, r = divmod(secs, 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m}m"


def _count_jobs(context) -> int:
    """Count total scheduled jobs."""
    try:
        jobs = context.application.job_queue.jobs() if context.application.job_queue else []
        return len(jobs) if jobs else 0
    except Exception as e:
        logger.warning(f"Error counting jobs: {e}")
        return 0


def _next_ritual(context):
    """Find the soonest scheduled 4:20 ritual across all hubs."""
    try:
        jobs = context.application.job_queue.jobs() if context.application.job_queue else []
        next_times = [j.next_t for j in jobs if j and j.name and j.name.startswith("420_") and j.next_t]
        if not next_times:
            logger.debug("No upcoming rituals found")
            return None, None
        nxt = min(next_times)
        hub = [j.name.replace("420_", "") for j in jobs if j.next_t == nxt]
        return hub[0] if hub else None, nxt
    except Exception as e:
        logger.exception(f"Error getting next ritual: {e}")
        return None, None


async def status(update, context):
    """Show bot health, scheduler status, price updates, and next ritual."""
    user_id = update.effective_user.id
    logger.info(f"Status command requested (user: {user_id})")
    
    try:
        # Get token and price anchor
        token = os.getenv("DEFAULT_TOKEN", "weedcoin").lower()
        anchor = kiss_anchor(token)
        
        # Get scheduler info
        job_count = _count_jobs(context)
        hub, nxt = _next_ritual(context)
        
        now = dt.datetime.now(dt.timezone.utc)
        nxt_txt = f"{nxt:%H:%M} UTC (in {_fmt_delta(nxt - now)})" if nxt else "Not scheduled"
        hub_txt = f" — {hub}" if hub else ""
        
        # Get Navigator's Blessing
        blessing = get_blessing()
        
        # Compose status message
        message = f"""
🌿⛵️ **Navigator Log — Toka v1**
{'─' * 40}

🟢 **BOT HEALTH**
Status: Online ✅
Uptime: Active

🕰 **SCHEDULER**
APScheduler: Active ✅
Jobs scheduled: {job_count}

📊 **PRICE ANCHOR**
Token: {token.upper()}
{anchor}

📅 **NEXT RITUAL**
Time: {nxt_txt}{hub_txt}
Frequency: Daily (4:20 AM/PM all zones)

────────────────────
**✨ Navigator's Blessing ✨**
{blessing}

*Use `/token [symbol]` for detailed charts*
*Use `/news` for market updates*
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ Status sent to user {user_id}")
        
    except Exception as e:
        logger.exception(f"Error in status command: {e}")
        await update.message.reply_text(
            "⚠️ Error generating status. Try again later.",
            parse_mode="Markdown"
        )
