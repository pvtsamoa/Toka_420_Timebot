import os, random
from services.ritual import build_ritual_text, load_media_bank
from services.dexscreener import get_anchor
from services.runtime import post_to_x

def _pick_tip():
    try:
        bank = load_media_bank()
        tips = (bank.get("safety") or []) + (bank.get("proverbs") or [])
        return random.choice(tips) if tips else "Shield up: keep seed phrases dry; ignore DM links."
    except Exception:
        return "Shield up: keep seed phrases dry; ignore DM links."

def build_x_text(hub_name: str, token_id: str):
    data = get_anchor(token_id)
    if not data:
        anchor = "$weedcoin — data n/a"
    else:
        price, change, vol = data["price"], data["change24"], data["vol24"]
        anchor = f"$weedcoin {change} • {price} • 24h vol {vol}"
    tip = _pick_tip()
    return (
        f"Tulou uso, Holy Minute in {hub_name}, 4:20 has arrived.\n"
        f"{anchor}\n"
        f"Toka says: {tip}\n"
        f"#Weedcoin #HolyMinute\n"
        f"@weedcoinog"
    )

async def ritual_call(context):
    hub_name = context.job.name.replace("420_", "")
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "weedcoin")
    # Telegram post (rich Navigator style handled elsewhere)
    text = build_ritual_text(hub_name, token)
    await context.bot.send_message(chat_id=os.getenv("TELEGRAM_GLOBAL_CHAT_ID"), text=text)
    # X relay (always $weedcoin ticker + vibe)
    try:
        post_to_x(build_x_text(hub_name, token))
    except Exception as e:
        print(f"[X relay error] {e}")
