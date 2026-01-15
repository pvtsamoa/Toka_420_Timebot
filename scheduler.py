import os
import json
import pytz
import datetime as dt
import logging
from telegram.ext import JobQueue

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)

def load_hubs():
    """Load hub configuration from data/hubs.json."""
    hubs_path = os.path.join(BASE_DIR, "data", "hubs.json")
    try:
        with open(hubs_path, "r", encoding="utf-8") as f:
            hubs = json.load(f)
            logger.debug(f"Loaded {len(hubs)} hubs from {hubs_path}")
            return hubs
    except FileNotFoundError:
        logger.error(f"❌ hubs.json not found at {hubs_path}")
        raise ValueError(f"Missing {hubs_path}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in hubs.json: {e}")
        raise ValueError(f"Invalid JSON in {hubs_path}") from e

def schedule_hubs(job_queue: JobQueue, callback):
    """Schedule daily 4:20 ritual for each hub."""
    try:
        hubs = load_hubs()
        logger.info(f"Scheduling rituals for {len(hubs)} hubs...")
        
        for hub in hubs:
            try:
                tz = pytz.timezone(hub["tz"])
                t420 = dt.time(hour=4, minute=20, tzinfo=tz)
                job_name = f"420_{hub['name']}"
                
                job_queue.run_daily(callback, time=t420, name=job_name)
                logger.info(f"✅ Scheduled {hub['name']} at 4:20 {hub['tz']}")
                
            except KeyError as e:
                logger.error(f"❌ Hub missing required field: {e}")
                raise
            except Exception as e:
                logger.exception(f"❌ Failed to schedule {hub.get('name', 'unknown')}: {e}")
                raise
        
        logger.info(f"✅ All {len(hubs)} rituals scheduled successfully")
        
    except Exception as e:
        logger.exception(f"💥 Failed to schedule hubs: {e}")
        raise
