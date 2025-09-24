import os, json, pytz, datetime as dt
from telegram.ext import JobQueue
BASE_DIR = os.path.dirname(__file__)
def load_hubs():
    with open(os.path.join(BASE_DIR, "data", "hubs.json"), "r", encoding="utf-8") as f:
        return json.load(f)
def schedule_hubs(job_queue: JobQueue, callback):
    for hub in load_hubs():
        tz = pytz.timezone(hub["tz"])
        t420 = dt.time(hour=4, minute=20, tzinfo=tz)
        job_queue.run_daily(callback, time=t420, name=f"420_{hub['name']}")
