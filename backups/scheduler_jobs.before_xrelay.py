from __future__ import annotations
from services.schedule_state import set_last_posted_420

import os
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import Optional, List, Dict, Any, Tuple, Callable

from zoneinfo import ZoneInfo
from telegram.ext import Application, ContextTypes

# Render layer (stable API from Step 1)
from services.render import render_ritual
from services.news import fetch_news
from services.news_render import render_news
from services.store.chat_state import get_chat_token, get_chat_lang, get_chat_show_moon
from services.market.anchor import get_market_anchor

from services.rituals.types import (
    RitualKey,
    RitualContext,
    HubInfo,
    MarketAnchor,
)

log = logging.getLogger(__name__)

# --- safe env int parser (prevents shell placeholder crashes) ---
def _safe_int_env(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default


# --------- Config surface (editable later or via env) ---------

# Fallback chat id if none was set via /setchat (can be overridden by env)
DEFAULT_CHAT_ID = _safe_int_env("TOKA_FALLBACK_CHAT_ID", 0)  # 0 means "unset"

# Minimal hubs set (add/remove freely). We keep LA first per Toka canon.
HUBS: List[Tuple[str, str]] = [
    ("Los Angeles", "America/Los_Angeles"),
    ("New York", "America/New_York"),
    ("Zurich", "Europe/Zurich"),
    ("Johannesburg", "Africa/Johannesburg"),
    ("Delhi", "Asia/Kolkata"),
]

# Token resolver hook (replace later with your per-chat store)
def _get_chat_token(chat_id: int) -> str:
    # 1) Per-chat env override (rare, but handy while wiring)
    env_key = f"TOKA_TOKEN_{chat_id}"
    if os.getenv(env_key):
        return os.getenv(env_key, "WEED")
    # 2) Global override
    return os.getenv("TOKA_DEFAULT_TOKEN", "WEED")

# Market KISS resolver hook (replace later with Dexscreener call)
def _get_market_anchor(symbol: str) -> MarketAnchor:
    """
    KISS market anchor: price, 24h %, 24h vol.
    Safe fallback: None fields -> templates print 'data unavailable'.
    """
    # Optional: quick env-based smoke values
    p = os.getenv("TOKA_SMOKE_PRICE")
    ch = os.getenv("TOKA_SMOKE_CHANGE_PCT")
    v = os.getenv("TOKA_SMOKE_VOL_24H")
    price = float(p) if p else None
    change = float(ch) if ch else None
    vol = float(v) if v else None
    return MarketAnchor(symbol=symbol, price=price, change_24h_pct=change, volume_24h=vol)

# --------- Mutable runtime state ---------
_TARGET_CHAT_ID: Optional[int] = None

def set_target_chat(chat_id: int) -> None:
    """
    Public setter used by commands/setchat.py.
    """
    global _TARGET_CHAT_ID
    _TARGET_CHAT_ID = int(chat_id)
    log.info("Target chat set to %s", _TARGET_CHAT_ID)

def _resolve_chat_id() -> int:
    """
    Priority: set_target_chat() -> env DEFAULT -> error
    """
    if _TARGET_CHAT_ID:
        return _TARGET_CHAT_ID
    if DEFAULT_CHAT_ID != 0:
        return DEFAULT_CHAT_ID
    raise RuntimeError(
        "No target chat set. Call /setchat or set TOKA_FALLBACK_CHAT_ID."
    )

# --------- Time helpers ---------

def _now_tz(tz: str) -> datetime:
    try:
        z = ZoneInfo(tz)
    except Exception:
        log.warning("Zone '%s' not found; falling back to UTC", tz)
        z = ZoneInfo('UTC')
    return datetime.now(z)

def _next_local_time(tz: str, hh: int, mm: int) -> datetime:
    """
    Return next occurrence of local hh:mm in the given IANA tz.
    """
    try:
        z = ZoneInfo(tz)
    except Exception:
        log.warning("Zone '%s' not found; scheduling in UTC", tz)
        z = ZoneInfo('UTC')
    now = datetime.now(z)
    candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate

# --------- Context builder ---------

def _build_ctx(hub_name: str, hub_tz: str, ritual_dt: datetime, chat_id: int) -> RitualContext:
    token = get_chat_token(chat_id)
    anchor = get_market_anchor(token)
    return RitualContext(
        hub=HubInfo(name=hub_name, tz=hub_tz),
        ritual_dt_iso=ritual_dt.isoformat(),
        chat_token=token,
        market=anchor,
        extra={},
    )

# --------- Bot send helper ---------

async def _send(app: Application, chat_id: int, text: str) -> None:
    await app.bot.send_message(chat_id=chat_id, text=text)

# --------- Job callbacks ---------

async def _job_pre_roll(context: ContextTypes.DEFAULT_TYPE) -> None:
    app: Application = context.application
    chat_id = _resolve_chat_id()
    hub_name = context.job.data["hub_name"]
    hub_tz = context.job.data["hub_tz"]
    run_dt_local = _now_tz(hub_tz).replace(second=0, microsecond=0)
    ctx = _build_ctx(hub_name, hub_tz, run_dt_local, chat_id)
    text = render_ritual(RitualKey.PRE_ROLL, ctx)
    await _send(app, chat_id, text)
    log.info("Sent Pre-Roll | hub=%s tz=%s chat=%s", hub_name, hub_tz, chat_id)

async def _job_holy_minute(context: ContextTypes.DEFAULT_TYPE) -> None:
    app: Application = context.application
    chat_id = _resolve_chat_id()
    hub_name = context.job.data["hub_name"]
    hub_tz = context.job.data["hub_tz"]
    run_dt_local = _now_tz(hub_tz).replace(second=0, microsecond=0)
    ctx = _build_ctx(hub_name, hub_tz, run_dt_local, chat_id)
    text = render_ritual(RitualKey.HOLY_MINUTE, ctx)
    await _send(app, chat_id, text)
    log.info("Sent Holy Minute | hub=%s tz=%s chat=%s", hub_name, hub_tz, chat_id)

# --------- Scheduler wiring ---------

def _schedule_for_hub(app: Application, hub_name: str, hub_tz: str) -> None:
    jq = app.job_queue
    # Pre-Roll @ 04:00 local
    next_pre = _next_local_time(hub_tz, 4, 0)
    # Holy Minute @ 04:20 local
    next_holy = _next_local_time(hub_tz, 4, 20)

    # Schedule next occurrences, then repeat daily
    jq.run_repeating(
        _job_pre_roll,
        interval=timedelta(days=1),
        first=next_pre.astimezone(ZoneInfo("UTC")),
        name=f"pre_roll::{hub_name}",
        data={"hub_name": hub_name, "hub_tz": hub_tz},
    )
    jq.run_repeating(
        _job_holy_minute,
        interval=timedelta(days=1),
        first=next_holy.astimezone(ZoneInfo("UTC")),
        name=f"holy_minute::{hub_name}",
        data={"hub_name": hub_name, "hub_tz": hub_tz},
    )

    log.info(
        "Scheduled hub=%s tz=%s | next preroll=%s | next holy=%s",
        hub_name, hub_tz, next_pre, next_holy
    )

def schedule_hubs(app: Application) -> None:
    """
    Public entry used by app.py.
    Schedules Pre-Roll (04:00) and Holy Minute (04:20) for each HUBS entry.
    """
    # Simply touching _resolve_chat_id here surfaces misconfig early (before first job fires)
    try:
        _ = _resolve_chat_id()
    except Exception as e:
        log.warning("Scheduler starting without target chat: %s", e)

    for hub_name, hub_tz in HUBS:
        _schedule_for_hub(app, hub_name, hub_tz)

# --------- Manual one-shot runners (optional) ---------

async def run_pre_roll_once(app: Application, hub_name: str, hub_tz: str) -> None:
    chat_id = _resolve_chat_id()
    ctx = _build_ctx(hub_name, hub_tz, _now_tz(hub_tz), chat_id)
    await _send(app, chat_id, render_ritual(RitualKey.PRE_ROLL, ctx))

async def run_holy_minute_once(app: Application, hub_name: str, hub_tz: str) -> None:
    chat_id = _resolve_chat_id()
    ctx = _build_ctx(hub_name, hub_tz, _now_tz(hub_tz), chat_id)
    await _send(app, chat_id, render_ritual(RitualKey.HOLY_MINUTE, ctx))

# --- Toka Voice hooks begin ---
from datetime import time
import os
from zoneinfo import ZoneInfo
try:
    from services.voice_toka import get_toka_line
except Exception:
    def get_toka_line(mode: str, **kwargs) -> str:
        return f"[Toka voice unavailable] mode={mode}"
_TARGET_CHAT_ID=None
def set_target_chat(chat_id:int|str)->int:
    global _TARGET_CHAT_ID
    try:_TARGET_CHAT_ID=int(chat_id)
    except Exception:_TARGET_CHAT_ID=chat_id
    return _TARGET_CHAT_ID
try:from config import SUA_CHAT_ID as _DEF_CHAT
except Exception:_DEF_CHAT=None
try:from config import FALLBACK_CHAT as _FALLBACK
except Exception:_FALLBACK=None
if _TARGET_CHAT_ID is None:
    import os;_TARGET_CHAT_ID=_DEF_CHAT or os.environ.get("TOKA_TARGET_CHAT") or _FALLBACK



async def job_toka_preroll(context):
    chat_id = _TARGET_CHAT_ID
    if not chat_id:
        return
    try:
        msg = render_ritual("preroll", chat_id)
    except Exception as e:
        msg = f"Toka drifted off — render error: {e}"
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def job_toka_holy(context):
    chat_id = _TARGET_CHAT_ID
    if not chat_id:
        return
    try:
        msg = render_ritual("holy_minute", chat_id)
    except Exception as e:
        msg = f"Toka drifted off — render error: {e}"
    await context.bot.send_message(chat_id=chat_id, text=msg)

    try:
        set_last_posted_420()
    except Exception:
        pass
def register_toka_voice_jobs(job_queue,tzname:str,price="$—",volume="—",change="—"):
    tz=ZoneInfo(tzname)
    job_queue.run_daily(job_toka_preroll,time(4,0,0,tzinfo=tz),name=f"toka_preroll_{tzname}",data={"price":price,"volume":volume,"change":change})
    job_queue.run_daily(job_toka_holy,time(4,20,0,tzinfo=tz),name=f"toka_holy_{tzname}",data={"price":price,"volume":volume,"change":change})
# --- Toka Voice hooks end ---


# Local 4:20 times for each market hub
HUB_TZS = {
    "asia": "Asia/Tokyo",
    "europe": "Europe/London",
    "americas": "America/New_York",
    "oceania": "Pacific/Apia",
}


async def _post_hub_news_420(context, hub: str):
    chat_id = get_target_chat()
    if not chat_id:
        return
    try:
        items = fetch_news(limit=5, lane="cannabis", hub=hub)
        header = f"⏰ 4:20 {hub.title()} Digest"
        msg = header + "\n" + render_news(items)
        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"🌊 Toka drifted on {hub} digest: {e}")

async def job_news_420_asia(context):    await _post_hub_news_420(context, "asia")
async def job_news_420_europe(context):  await _post_hub_news_420(context, "europe")
async def job_news_420_americas(context):await _post_hub_news_420(context, "americas")
async def job_news_420_oceania(context): await _post_hub_news_420(context, "oceania")
