from telegram import Update
from telegram.ext import ContextTypes
from services.store.chat_state import set_chat_lang, get_chat_lang

HELP = "Usage: /lang sm|en\nExample: /lang sm"

async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    args = context.args or []
    if not args:
        await update.message.reply_text(f"Current: {get_chat_lang(chat_id)}\n{HELP}")
        return
    v = args[0].lower().strip()
    if v not in ("sm","en"):
        await update.message.reply_text(HELP)
        return
    set_chat_lang(chat_id, v)
    await update.message.reply_text(f"✅ Language set for this chat: {v}")
