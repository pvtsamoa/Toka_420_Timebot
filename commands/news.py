from telegram import Update
from telegram.ext import ContextTypes
from services.news import fetch_canna_crypto
from services.render import news_text

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = fetch_canna_crypto(max_per_source=3)
    await update.message.reply_text(news_text(results))
