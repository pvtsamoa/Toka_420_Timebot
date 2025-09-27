from telegram import Update
from telegram.ext import ContextTypes
from config import RITUAL_TOKEN
from services.price import get_anchor

async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tok = (context.args[0] if context.args else RITUAL_TOKEN).upper()
    anchor = get_anchor(tok)
    msg = (f"💱 {tok}\n"
           f"Price: {anchor['price']}\n"
           f"24h: {anchor['change_24h']}\n"
           f"24h Vol: {anchor['volume_24h']}")
        f"Market Cap: {anchor.get('market_cap', 'n/a')}
"
    await update.message.reply_text(msg)
