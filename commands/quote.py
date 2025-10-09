from telegram import Update
from telegram.ext import ContextTypes
from services.store import get_chat_token
from services.anchors import get_anchor
from services.anchor_render import render_kiss_anchor
async def quote(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    q=context.args[0] if context.args else get_chat_token(chat_id)
    try:
        a=get_anchor(q)
        line=render_kiss_anchor(a["symbol"],a["price"],a["change24h_pct"],a["volume24h_usd"])
        await update.message.reply_text(line)
    except Exception as e:
        await update.message.reply_text(f"Could not fetch anchor for '{q}': {e}")
