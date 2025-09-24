import pytz
from datetime import time as dtime
from telegram.ext import JobQueue

from scheduler.jobs import make_preroll_job, make_ritual_job
from config import SETTINGS

def register_jobs(app):
    tz = pytz.timezone("America/Los_Angeles")

    # ✅ Ensure job_queue exists
    jq = app.job_queue or JobQueue()
    if app.job_queue is None:
        jq.set_application(app)
        jq.start()

    # Pre-roll at 04:00
    preroll_cb = make_preroll_job(app.bot.send_message)
    jq.run_daily(preroll_cb, dtime(4, 0, tzinfo=tz))

    # Ritual at 04:20
    ritual_cb = make_ritual_job(app.bot.send_message)
    jq.run_daily(ritual_cb, dtime(4, 20, tzinfo=tz))

    return jq
