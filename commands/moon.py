from telegram import Update
from telegram.ext import ContextTypes
from services.store.chat_state import set_chat_show_moon, get_chat_show_moon

HELP = "Usage: /moon on|off\nExample: /moon on"

async def moon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    args = context.args or []
    if not args:
        cur = "on" if get_chat_show_moon(chat_id) else "off"
        await update.message.reply_text(f"Current: {cur}\n{HELP}")
        return
    v = args[0].lower().strip()
    if v in ("on","true","yes","1"):
        set_chat_show_moon(chat_id, True)
        await update.message.reply_text("✅ Moon line enabled for this chat.")
    elif v in ("off","false","no","0"):
        set_chat_show_moon(chat_id, False)
        await update.message.reply_text("✅ Moon line disabled for this chat.")
    else:
        await update.message.reply_text(HELP)
