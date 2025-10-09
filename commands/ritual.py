from telegram import Update
from telegram.ext import ContextTypes
from services.render import render_ritual
VALID = {"preroll","holy_minute","market_anchor","bongnite"}
async def ritual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = (context.args[0].lower() if context.args else "market_anchor")
    if mode not in VALID:
        await update.message.reply_text("Usage:\\n/ritual [preroll|holy_minute|market_anchor|bongnite]")
        return
    chat_id = update.effective_chat.id
    await update.message.reply_text(render_ritual(mode, chat_id))
