from telegram import Update
from telegram.ext import ContextTypes
from config import RITUAL_TOKEN
from services.price import get_anchor
from services.render import token_text

async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tok = (context.args[0] if context.args else RITUAL_TOKEN).upper()
        anchor = get_anchor(tok)
        await update.message.reply_text(token_text(tok, anchor))
    except Exception as e:
        await update.message.reply_text(f"Token error: {e}")
