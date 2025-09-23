from telegram import Update
from telegram.ext import ContextTypes
from .base import SetQuery
from services.price import get_anchor
from services.persona import toka_anchor_line
async def token_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    q = " ".join(context.args).strip() or "Weedcoin"
    SetQuery(chat_id, q)
    anchor = get_anchor(q)
    if anchor: await update.message.reply_text(toka_anchor_line(q, anchor))
    else:      await update.message.reply_text(f"Token set to {q}. ⚠️ No anchor yet.")
