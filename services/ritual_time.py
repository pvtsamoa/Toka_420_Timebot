import os
from services.ritual import build_ritual_text
from services.runtime import post_to_x
async def ritual_call(context):
    hub_name = context.job.name.replace("420_", "")
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "WEED")
    text = build_ritual_text(hub_name, token)
    await context.bot.send_message(chat_id=os.getenv("TELEGRAM_GLOBAL_CHAT_ID"), text=text)
    try: post_to_x(text)
    except Exception as e: print(f"[X relay error] {e}")
