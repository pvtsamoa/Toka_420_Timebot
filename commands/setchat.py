from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import set_target_chat
async def setchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage:\\n/setchat <chat_id>")
        return
    try: cid = int(context.args[0])
    except Exception: cid = context.args[0]
    set_target_chat(cid)
    await update.message.reply_text(f"Target chat set → {cid}")
