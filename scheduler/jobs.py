import logging, time
from typing import Callable
from config import SETTINGS
from services.ritual import compose_preroll, compose_ritual

log = logging.getLogger("jobs")

def make_preroll_job(send_fn: Callable[[int,str], None]):
    async def job(ctx):
        chat_id = ctx.job.chat_id
        hub = {"name": ctx.job.name.split("-")[1] if ctx.job and ctx.job.name else "Hub", "tz": ""}  # best effort
        text = compose_preroll(hub, SETTINGS.WEEDCOIN_TOKEN)
        await send_fn(chat_id, text)
        st = _get_state()
        st["last_preroll"] = time.time()
        _set_state(st)
    return job

def make_ritual_job(send_fn: Callable[[int,str], None]):
    async def job(ctx):
        chat_id = ctx.job.chat_id
        # try to infer hub name from job name; if not present, fallback
        hub_name = "Hub"
        if ctx.job and ctx.job.name and "-" in ctx.job.name:
            try:
                hub_name = ctx.job.name.split("-")[1]
            except Exception:
                pass
        hub = {"name": hub_name, "tz": ""}  # tz used only for pretty time inside compose
        text = compose_ritual(hub, SETTINGS.WEEDCOIN_TOKEN)
        await send_fn(chat_id, text)
        st = _get_state()
        st["last_ritual"] = time.time()
        _set_state(st)
    return job

# simple local state access using existing KV
from services.storage import KV
def _get_state(): 
    try: return KV.get()
    except Exception: return {}
def _set_state(s):
    try: KV.set(s)
    except Exception: pass
