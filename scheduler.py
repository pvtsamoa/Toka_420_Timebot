import os
import json
import pytz
import datetime as dt
import logging
import asyncio
import inspect
from types import SimpleNamespace

logger = logging.getLogger(__name__)

# scheduler.py lives at project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# All bot JSON config lives in /media
HUBS_PATH = os.path.join(PROJECT_ROOT, "media", "hubs.json")

JOB_PREFIX = "hub420:"


def load_hubs():
    logger.info("Loading hubs from: %s", HUBS_PATH)

    try:
        with open(HUBS_PATH, "r", encoding="utf-8") as f:
            hubs = json.load(f)
    except FileNotFoundError:
        logger.error("hubs.json not found at %s", HUBS_PATH)
        raise ValueError(f"Missing {HUBS_PATH}")
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in hubs.json: %s", e)
        raise ValueError(f"Invalid JSON in {HUBS_PATH}") from e

    if not isinstance(hubs, list):
        raise ValueError("hubs.json must be a JSON list")

    # allow enabled=false
    enabled = [h for h in hubs if h.get("enabled", True) is True]

    logger.info("Loaded %d hubs (%d enabled)", len(hubs), len(enabled))
    return enabled


def _build_ptb_context(app, data: dict):
    """
    Minimal PTB-like CallbackContext shim.
    """
    return SimpleNamespace(
        job=SimpleNamespace(data=data),
        application=app,
        bot=getattr(app, "bot", None),
    )


def schedule_hubs(scheduler_or_jobqueue, callback, app=None):
    """
    Schedule ONE 4:20 per timezone.
    At runtime, ritual_call chooses which HUB and which CITY speaks.
    """
    hubs = load_hubs()

    is_ptb_jobqueue = hasattr(scheduler_or_jobqueue, "run_daily")
    is_apscheduler = hasattr(scheduler_or_jobqueue, "add_job")

    if not (is_ptb_jobqueue or is_apscheduler):
        raise TypeError("scheduler must be JobQueue or APScheduler")

    if is_apscheduler and app is None:
        raise ValueError("APScheduler requires app=Application")

    # Group hubs by timezone
    tz_map = {}
    for hub in hubs:
        tz = hub.get("tz")
        hub_id = hub.get("hub")
        cities = hub.get("cities")

        if not tz or not hub_id or not isinstance(cities, list):
            raise KeyError(f"Invalid hub definition: {hub}")

        tz_map.setdefault(tz, []).append(hub)

    logger.info("Found %d timezones to schedule", len(tz_map))

    scheduled = 0

    for tz_name, hubs_in_tz in tz_map.items():
        tz = pytz.timezone(tz_name)

        payload = {
            "tz": tz_name,
            "hubs": hubs_in_tz
        }

        job_name = f"{JOB_PREFIX}{tz_name}"

        if is_ptb_jobqueue:
            t420 = dt.time(hour=4, minute=20)

            job = scheduler_or_jobqueue.run_daily(
                callback,
                time=t420,
                timezone=tz,
                name=job_name,
                data=payload,
            )

            logger.info(
                "Scheduled %s at 04:20 | hubs=%d | next=%s",
                tz_name,
                len(hubs_in_tz),
                getattr(job, "next_t", None),
            )
            scheduled += 1
            continue

        # APScheduler path
        from apscheduler.triggers.cron import CronTrigger

        async def _run(payload=payload):
            ctx = _build_ptb_context(app, payload)
            if inspect.iscoroutinefunction(callback):
                await callback(ctx)
            else:
                callback(ctx)

        def _fire():
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_run())
            except RuntimeError:
                asyncio.run(_run())

        job = scheduler_or_jobqueue.add_job(
            _fire,
            CronTrigger(hour=4, minute=20, timezone=tz),
            id=job_name,
            name=job_name,
            replace_existing=True,
        )

        logger.info(
            "Scheduled %s at 04:20 | hubs=%d | next=%s",
            tz_name,
            len(hubs_in_tz),
            getattr(job, "next_run_time", None),
        )
        scheduled += 1

    logger.info("All timezone rituals scheduled: %d", scheduled)
