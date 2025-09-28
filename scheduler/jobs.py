from datetime import time as dtime, datetime, timedelta
from typing import Optional, Tuple
import pytz

from telegram.ext import JobQueue, ContextTypes

from config import HUBS, RITUAL_TOKEN, X_RELAY_DEFAULT
from services.price import get_anchor
from services.relay import XRelay
from services.render import preroll_text, holy_text
from services.log import get_logger

logger = get_logger()

_target_chat_id: int | None = None

def set_target_chat(chat_id: int):
    global _target_chat_id
    _target_chat_id = int(chat_id)
    logger.info("Target chat set to %s", _target_chat_id)

def get_target_chat() -> int | None:
    return _target_chat_id


# Global, single X relay instance used by /x and scheduler
_xrelay = XRelay(X_RELAY_DEFAULT)

# (kind, "Hub @ ISO")
_last_call: Optional[Tuple[str, str]] = None


def last_call_info() -> Optional[Tuple[str, str]]:
    return _last_call


def x_status() -> bool:
    return _xrelay.enabled


async def _send(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int | None, text: str):
    try:
        target = chat_id if chat_id is not None else get_target_chat()
        await ctx.bot.send_message(chat_id=target, text=text)
    except Exception as e:
        logger.exception("Telegram send failed: %s", e)


async def _preroll_cb(ctx: ContextTypes.DEFAULT_TYPE, hub: str, chat_id: int):
    global _last_call
    _last_call = ("preroll", f"{hub} @ {datetime.utcnow().isoformat(timespec=seconds)}Z")
    logger.info("PREROLL fired: hub=%s", hub)
    await _send(ctx, None, preroll_text(hub))


async def _holy_cb(ctx: ContextTypes.DEFAULT_TYPE, hub: str, chat_id: int):
    global _last_call
    anchor = get_anchor(RITUAL_TOKEN)
    text = holy_text(hub, RITUAL_TOKEN, anchor)
    _last_call = ("holy", f"{hub} @ {datetime.utcnow().isoformat(timespec=seconds)}Z")
    logger.info("HOLY fired: hub=%s | anchor=%s", hub, anchor)
    await _send(ctx, None, text)
    _xrelay.post(text)


def _next_local_dt(tz: pytz.timezone, hour: int, minute: int) -> datetime:
    """Compute the next occurrence of hour:minute in given tz, return tz-aware dt."""
    now_local = datetime.now(tz)
    candidate = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now_local:
        candidate += timedelta(days=1)
    return candidate


def schedule_hubs(jobq: JobQueue, chat_id: int):
    """Register daily jobs for each hub at 4:00 and 4:20 local times."""
    if jobq is None:
        raise RuntimeError("JobQueue is not configured (install PTB with [job-queue]).")

    for hub in HUBS:
        tz = pytz.timezone(hub.tzid)

        # Pre-compute next times (for logging)
        nxt_pre = _next_local_dt(tz, 4, 0)
        nxt_holy = _next_local_dt(tz, 4, 20)

        # Register jobs
        jobq.run_daily(lambda c, h=hub.name: _preroll_cb(c, h, chat_id),
                       time=dtime(4, 0, tzinfo=tz), name=f"preroll-{hub.name}")
        jobq.run_daily(lambda c, h=hub.name: _holy_cb(c, h, chat_id),
                       time=dtime(4, 20, tzinfo=tz), name=f"holy-{hub.name}")

        logger.info(
            "Scheduled hub=%s tz=%s | next preroll=%s | next holy=%s",
            hub.name, hub.tzid,
            nxt_pre.isoformat(timespec="minutes"),
            nxt_holy.isoformat(timespec="minutes"),
        )


def next_scheduled_summary() -> str:
    """Return soonest of next preroll/holy across hubs, as a friendly string."""
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    soonest = None
    label = ""
    for hub in HUBS:
        tz = pytz.timezone(hub.tzid)
        local_now = now_utc.astimezone(tz)
        for hh, mm, kind in ((4, 0, "preroll"), (4, 20, "holy")):
            t = local_now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if t <= local_now:
                t += timedelta(days=1)
            t_utc = t.astimezone(pytz.utc)
            if (soonest is None) or (t_utc < soonest):
                soonest = t_utc
                label = f"{kind} @ {hub.name}"
    if soonest:
        delta = soonest - now_utc
        return f"{label} in {delta}"
    return "n/a"
