from __future__ import annotations
from services.anchors import get_anchor
from services.voice_toka import get_toka_line
from services.moon import toka_moon_sentence

def render_ritual(mode: str, chat_id: int | str | None = None) -> str:
    """
    Builds text for the ritual calls and status checks.
    """
    token = None
    if not token:
        return (
            "Tulou lava, navigator — no token is set for this crew.\n"
            "Use /token <symbol> first."
        )

    try:
        anchor = get_anchor(token)
    except Exception as e:
        return f"Toka drifts in silence — failed to fetch anchor for {token}: {e}"

    # Choose line by mode
    if mode == "preroll":
        line = get_toka_line("preroll")
    elif mode == "holy_minute":
        line = get_toka_line("holy_minute")
    elif mode == "market_anchor":
        line = get_toka_line("market_anchor")
    elif mode == "bongnite":
        line = get_toka_line("bongnite")
    else:
        line = "Toka hums in the fog — unknown ritual."

    # Optional moon wisdom
    try:
        moon_line = toka_moon_sentence()
    except Exception:
        moon_line = ""

    msg = f"{line}\n{anchor}"
    if moon_line:
        msg += f"\n\n{moon_line}"

    return msg

from services.anchors import get_anchor
from services.store import get_chat_token
from services.token_line import render_token_line

def render_token(chat_id: int, query: str|None = None) -> str:
    """
    Build the /token line.
    - If query provided, use that; else use chat's token; else instruct setup.
    """
    q = (query or "").strip()
    if not q:
        q = get_chat_token(chat_id)
    if not q:
        return ("Tulou lava, navigator — no token set for this chat.\n"
                "Use /token <symbol|address> or set TOKEN_DEFAULT.")
    try:
        a = get_anchor(q)
    except Exception as e:
        return f"Toka drifts in silence — failed to fetch anchor for {q}: {e}"
    return render_token_line(a.get("symbol"), a.get("price"),
                             a.get("change24h_pct"), a.get("mcap_usd"),
                             a.get("fdv_usd"))
