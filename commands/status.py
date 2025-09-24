import os
from services.ritual import kiss_anchor
async def status(update, context):
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "WEED")
    await update.message.reply_text(f"⏱ Status OK\n📈 {kiss_anchor(token)}")
