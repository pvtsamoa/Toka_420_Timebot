from telegram import Update
from telegram.ext import ContextTypes
from services.store.chat_state import set_chat_hub

VALID = {"asia","europe","americas","oceania"}

async def sethub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hub = (context.args[0].lower() if context.args else "").strip()
    if hub not in VALID:
        await update.message.reply_text(
            "Usage: /sethub <asia|europe|americas|oceania>\n"
            "Example: /sethub europe"
        )
        return
    try:
        set_chat_hub(update.effective_chat.id, hub)
        await update.message.reply_text(f"Default hub set → {hub}")
    except Exception as e:
        await update.message.reply_text(f"Could not set hub: {e}")
