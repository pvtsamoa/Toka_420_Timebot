from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import last_call_info, next_scheduled_summary, x_status
from services.render import status_text

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lc = last_call_info()
    # Only call it "Last blunt" if the last call was a holy post
    last = lc[1] if (lc and lc[0] == "holy") else "none"
    nxt  = next_scheduled_summary()
    await update.message.reply_text(status_text(last, nxt, x_status()))
