from telegram import Update
from telegram.ext import ContextTypes
from services.render import status_text

# Import scheduler helpers; if something is missing, provide safe fallbacks
try:
    from scheduler.jobs import last_call_info, next_scheduled_summary, x_status
except Exception:
    def last_call_info():
        return None
    def next_scheduled_summary():
        return "n/a"
    def x_status():
        return False

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lc = last_call_info()
        # Only call it "Last blunt" if the last call was a holy post
        last = lc[1] if (lc and lc[0] == "holy") else "none"
        nxt  = next_scheduled_summary()
        await update.message.reply_text(status_text(last, nxt, x_status()))
    except Exception as e:
        # Surface the problem so we can fix quickly
        await update.message.reply_text(f"Status error: {e}")
