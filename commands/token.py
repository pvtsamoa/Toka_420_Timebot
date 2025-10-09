from telegram import Update
from telegram.ext import ContextTypes
from services.render import render_token
from services.store import set_chat_token

async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    q = " ".join(context.args).strip() if context.args else ""
    # If user gives a symbol/address, also store it for this chat
    if q:
        set_chat_token(chat_id, q)
    msg = render_token(chat_id, q or None)
    await update.message.reply_text(msg)
