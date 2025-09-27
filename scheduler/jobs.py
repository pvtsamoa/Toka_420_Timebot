from datetime import time, datetime, timedelta
from typing import Optional, Tuple
import pytz
from telegram.ext import JobQueue, ContextTypes
from config import HUBS, RITUAL_TOKEN, X_RELAY_DEFAULT
from services.price import get_anchor
from services.relay import XRelay
from services.render import preroll_text, holy_text
from services.log import get_logger

logger = get_logger()
_xrelay = XRelay(X_RELAY_DEFAULT)
_last_call: Optional[Tuple[str, str]] = None  # (kind, "Hub @ ISO")

def last_call_info() -> Optional[Tuple[str, str]]:
    return _last_call

def x_status() -> bool:
    return _xrelay.enabled

async def _send(ctx: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    try:
        await ctx.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.exception("Telegram send failed: %s", e)

async def _preroll_cb(ctx: ContextTypes.DEFAULT_TYPE, hub: str, chat_id: int):
    global _last_call
    _last_call = ("preroll", f"{hub} @ {datetime.now().isoformat(timespec='seconds')}")
    await _send(ctx, chat_id, preroll_text(hub))

async def _holy_cb(ctx: ContextTypes.DEFAULT_TYPE, hub: str, chat_id: int):
    global _last_call
    anchor = get_anchor(RITUAL_TOKEN)
    text = holy_text(hub, RITUAL_TOKEN, anchor)
    _last_call = ("holy", f"{hub} @ {datetime.now().isoformat(timespec='seconds')}")
    await _send(ctx, chat_id, text)
    _xrelay.post(text)

def schedule_hubs(jobq: JobQueue, chat_id: int):
    for hub in HUBS:
        tz = pytz.timezone(hub.tzid)
        jobq.run_daily(lambda c, h=hub.name: _preroll_cb(c, h, chat_id),
                       time=time(4, 0, tzinfo=tz), name=f"preroll-{hub.name}")
        jobq.run_daily(lambda c, h=hub.name: _holy_cb(c, h, chat_id),
                       time=time(4, 20, tzinfo=tz), name=f"holy-{hub.name}")

def next_scheduled_summary() -> str:
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    soonest = None; label = ""
    for hub in HUBS:
        tz = pytz.timezone(hub.tzid)
        local_now = now_utc.astimezone(tz)
        for hh, mm, kind in ((4,0,"preroll"), (4,20,"holy")):
            t = local_now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if t <= local_now:
                t = t + timedelta(days=1)
            if (soonest is None) or (t < soonest):
                soonest = t; label = f"{kind} @ {hub.name}"
    if soonest:
        delta = soonest - now_utc.astimezone(soonest.tzinfo)
        return f"{label} in {delta}"
    return "n/a"
