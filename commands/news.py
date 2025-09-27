from telegram import Update
from telegram.ext import ContextTypes
from services.news import fetch_canna_crypto

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = fetch_canna_crypto()
    lines = ["🗞️ Cannabis × Crypto headlines"]
    for src, items in results.items():
        if not items:
            continue
        lines.append(f"- {src}:")
        for title, link in items:
            lines.append(f"  • {title}\n    {link}")
    if len(lines) == 1:
        lines.append("(no relevant headlines right now)")
    await update.message.reply_text("\n".join(lines))
