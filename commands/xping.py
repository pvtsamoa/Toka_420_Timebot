from telegram import Update
from telegram.ext import ContextTypes
from config import HAS_X
from services.runtime import post_to_x

async def xping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not HAS_X:
        await update.message.reply_text("❌ X relay is disabled. Add keys to .env and restart.")
        return
    text = "🌊 Toka420 test relay — X ping"
    ok, msg = post_to_x(text)
    await update.message.reply_text(("✅ " if ok else "⚠️ ") + f"X relay: {msg}")
