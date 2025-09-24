from datetime import datetime, timedelta
import pytz

DEFAULT_TZ = "America/Los_Angeles"

def _local_now(tz: str) -> datetime:
    return datetime.now(pytz.timezone(tz))

def next_times(tz: str = DEFAULT_TZ):
    """Return (next_preroll_dt, next_ritual_dt) as timezone-aware datetimes."""
    z = pytz.timezone(tz)
    now = _local_now(tz)

    # candidate today at 04:20 and 04:00
    rt = z.localize(datetime(now.year, now.month, now.day, 4, 20, 0))
    pr = z.localize(datetime(now.year, now.month, now.day, 4, 0, 0))

    if now <= rt:
        next_ritual = rt
        # if it's already past 4:00 but before 4:20, pre-roll is "tomorrow" 4:00
        next_preroll = pr if now <= pr else z.localize(datetime(now.year, now.month, now.day, 4, 0, 0)) + timedelta(days=1)
    else:
        # tomorrow
        tomorrow = now + timedelta(days=1)
        next_ritual = z.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, 20, 0))
        next_preroll = z.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 4, 0, 0))

    return (next_preroll, next_ritual)

def fmt_when(dt: datetime):
    """Return 'HH:MM (in Xm)' formatted string for a tz-aware datetime relative to now."""
    tz = dt.tzinfo
    now = datetime.now(tz)
    delta = dt - now
    total = int(delta.total_seconds())
    sign = "" if total >= 0 else "-"
    total = abs(total)
    h, r = divmod(total, 3600)
    m, _ = divmod(r, 60)
    return f"{dt.strftime('%H:%M')} (in {sign}{h}h {m}m)"
