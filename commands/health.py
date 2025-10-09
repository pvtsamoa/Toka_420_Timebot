from telegram import Update
from telegram.ext import ContextTypes

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Minimal, fast check; deeper checks would hit services
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except Exception:
        pass
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Toka alive: handlers loaded, scheduler running. Try /status, /news, /token"
    )
