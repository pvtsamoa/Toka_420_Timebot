import os, logging
from services.ritual import build_ritual_text
from services.pools import pick_combo
from services.runtime import post_to_x, build_x_text

async def ritual_call(context):
    """
    JobQueue callback: post the Holy Minute to the configured Telegram chat,
    then relay to X.
    """
    hub_name = (context.job.name or "").replace("420_", "")
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "weedcoin")

    text = build_ritual_text(hub_name, token)

    raw = (os.getenv("TELEGRAM_GLOBAL_CHAT_ID") or "").strip()
    if not raw:
        logging.error("TELEGRAM_GLOBAL_CHAT_ID missing at send time.")
        return
    first = raw.split(",")[0].strip()
    try:
        chat_id = int(first)
    except ValueError:
        logging.error("Bad TELEGRAM_GLOBAL_CHAT_ID value: %r", raw)
        return

    logging.info("Sending ritual to chat_id=%s (hub=%s)", chat_id, hub_name)
    await context.bot.send_message(chat_id=chat_id, text=text)

    try:
        if post_to_x:
            edu, saf = pick_combo()
            tip = edu or saf
            post_to_x(build_x_text(hub_name, token, tip))
    except Exception as e:
        logging.warning("[X relay error] %s", e)
