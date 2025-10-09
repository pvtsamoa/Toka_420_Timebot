from typing import List, Tuple
from telegram import Update
from telegram.ext import ContextTypes
from services.rituals.types import RitualKey, RitualContext, HubInfo
from services.market.anchor import get_market_anchor
from services.render import render_ritual
from scheduler.jobs import HUBS, _next_local_time
from services.store.chat_state import get_global_target_chat
import os

def _is_admin(chat_id: int) -> bool:
    env_admin = os.getenv("TOKA_ADMIN_CHAT_ID")
    if env_admin:
        try:
            if chat_id == int(env_admin):
                return True
        except Exception:
            pass
    try:
        stored = get_global_target_chat(0)
        if stored != 0 and chat_id == stored:
            return True
    except Exception:
        pass
    return False

def _fmt_schedule_lines() -> str:
    lines: List[str] = ["🗓️ Schedule (next local times)"]
    for hub_name, hub_tz in HUBS:
        pre  = _next_local_time(hub_tz, 4, 0)
        holy = _next_local_time(hub_tz, 4, 20)
        lines.append(f"• {hub_name} ({hub_tz})  Pre-Roll: {pre}  |  Holy: {holy}")
    return "\n".join(lines)

def _ritual_from_key(s: str) -> RitualKey:
    s = s.lower().strip()
    if s in ("pre_roll","pre","preroll","pre-roll"): return RitualKey.PRE_ROLL
    if s in ("holy_minute","holy","minute","hm"):    return RitualKey.HOLY_MINUTE
    raise ValueError("Unknown ritual key. Use pre_roll or holy_minute.")

def _hub_match(name: str) -> Tuple[str, str]:
    for hn, tz in HUBS:
        if name == hn: return hn, tz
    name_low = name.lower()
    for hn, tz in HUBS:
        if hn.lower().startswith(name_low): return hn, tz
    raise ValueError("Hub not found. Use an exact or unique prefix of hub name.")

def _dry_render(hub_name: str, hub_tz: str, token: str, rk: RitualKey) -> str:
    anchor = get_market_anchor(token)
    ctx = RitualContext(
        hub=HubInfo(name=hub_name, tz=hub_tz),
        ritual_dt_iso=_next_local_time(hub_tz, 4, 20).isoformat(),
        chat_token=token,
        market=anchor,
        extra={}
    )
    text = render_ritual(rk, ctx)
    return f"🧪 DRY PREVIEW — {rk.value} | {hub_name}\n{text}"

HELP = (
    "🔐 /admin (admin-only)\n"
    "Subcommands:\n"
    "  schedule list\n"
    "  ritual_now pre_roll|holy_minute [hub]\n"
    "Examples:\n"
    "  /admin schedule list\n"
    "  /admin ritual_now pre_roll Los Angeles\n"
    "  /admin ritual_now holy_minute New York"
)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat: return
    if not _is_admin(chat.id): return

    args = context.args or []
    if not args:
        await context.bot.send_message(chat_id=chat.id, text=HELP)
        return

    cmd, *rest = [a for a in args if a]
    cmd = cmd.lower()

    if cmd == "schedule" and rest[:1] == ["list"]:
        await context.bot.send_message(chat_id=chat.id, text=_fmt_schedule_lines()); return

    if cmd == "ritual_now":
        if not rest:
            await context.bot.send_message(chat_id=chat.id, text="Usage: /admin ritual_now pre_roll|holy_minute [hub]"); return
        try:
            rk = _ritual_from_key(rest[0])
        except ValueError as e:
            await context.bot.send_message(chat_id=chat.id, text=str(e)); return
        if len(rest) >= 2:
            try:
                hub_name, hub_tz = _hub_match(" ".join(rest[1:]).strip())
            except ValueError as e:
                await context.bot.send_message(chat_id=chat.id, text=str(e)); return
        else:
            hub_name, hub_tz = HUBS[0]
        token = os.getenv("TOKA_DEFAULT_TOKEN", "WEEDCOIN")  # dry preview uses default
        preview = _dry_render(hub_name, hub_tz, token, rk)
        await context.bot.send_message(chat_id=chat.id, text=preview); return

    await context.bot.send_message(chat_id=chat.id, text=HELP)
