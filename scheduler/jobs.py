import logging
from typing import Callable
from services.price import get_anchor, default_query
from services.persona import toka_anchor_line
log = logging.getLogger("jobs")
def make_preroll_job(send_fn: Callable[[int,str], None], get_query: Callable[[int], str] = default_query):
    async def job(ctx):
        chat_id = ctx.job.chat_id; q = get_query(chat_id)
        await send_fn(chat_id, f"⛵️ Pre-roll @ 4:00 — setting sail for 4:20 | token: {q}")
    return job
def make_ritual_job(send_fn: Callable[[int,str], None], get_query: Callable[[int], str] = default_query):
    async def job(ctx):
        chat_id = ctx.job.chat_id; q = get_query(chat_id)
        anchor = get_anchor(q)
        if not anchor:
            await send_fn(chat_id, f"⚠️ Anchor unavailable for {q}. Keep calm, paddle on."); return
        await send_fn(chat_id, toka_anchor_line(q, anchor))
    return job
