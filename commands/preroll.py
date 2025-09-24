import os, datetime as dt, pytz
from services.ritual_time import ritual_call

def _tz():
    name = os.getenv("TZ", "UTC")
    try:
        return pytz.timezone(name)
    except Exception:
        return pytz.UTC

def _next_3am(tz):
    now = dt.datetime.now(tz)
    target = tz.localize(dt.datetime(now.year, now.month, now.day, 3, 0, 0))
    if now >= target:
        target = target + dt.timedelta(days=1)
    return target

async def preroll(update, context):
    tz = _tz()
    when_local = _next_3am(tz)
    # JobQueue expects an aware UTC datetime
    when_utc = when_local.astimezone(pytz.UTC)

    # Name starts with "420_" so ritual_call formats hub label nicely
    job_name = "420_PrEROLL"
    context.application.job_queue.run_once(
        ritual_call,
        when=when_utc,
        name=job_name,
    )

    await update.message.reply_text(
        f"🧪 Preroll scheduled for {when_local.strftime('%Y-%m-%d %H:%M')} {tz.zone} "
        f"({when_utc.strftime('%H:%M')} UTC). I’ll post at that time."
    )
