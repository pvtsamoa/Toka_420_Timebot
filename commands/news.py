from telegram import Update
from telegram.ext import ContextTypes
from services.news import sources_by_region

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    regions = sources_by_region()
    lines = ["🗞️ News sources by region:"]
    for r, srcs in regions.items():
        lines.append(f"- {r}: " + ", ".join(srcs))
    await update.message.reply_text("\n".join(lines))
