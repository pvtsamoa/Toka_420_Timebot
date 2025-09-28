from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import set_target_chat

async def setchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /setchat this  -> use current chat
    # /setchat -1001234567890 -> use provided id
    if not context.args:
        await update.message.reply_text("Usage: /setchat this | /setchat <numeric_chat_id>")
        return
    arg = context.args[0].strip().lower()
    try:
        if arg == "this":
            cid = update.effective_chat.id
        else:
            cid = int(arg)
        set_target_chat(cid)
        await update.message.reply_text(f"✅ Target chat set to {cid}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to set chat: {e}")
