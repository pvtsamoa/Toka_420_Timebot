from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import last_holy_info, next_holy_summary, x_status

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = last_holy_info() or "none"
    nxt  = next_holy_summary()
    xflag = "ON" if x_status() else "OFF"
    msg = (
        "✅ Toka 420 TimeBot — status\n"
        f"Last 4:20: {last}\n"
        f"Next 4:20: {nxt}\n"
        f"X relay: {xflag}"
    )
    await update.message.reply_text(msg)
