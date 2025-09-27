from telegram import Update
from telegram.ext import ContextTypes
from services.news import sources_by_region
from scheduler.jobs import last_call_info, next_scheduled_summary, x_status

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lc = last_call_info()
    last_line = f"{lc[0]} — {lc[1]}" if lc else "none"
    nxt = next_scheduled_summary()
    srcs = ", ".join(sorted(set(sum((v for v in sources_by_region().values()), []))))
    xflag = "ON" if x_status() else "OFF"
    msg = (
        "✅ Toka 420 TimeBot — status\n"
        f"Last call: {last_line}\n"
        f"Next: {nxt}\n"
        f"News sources: {srcs}\n"
        f"X relay: {xflag}"
    )
    await update.message.reply_text(msg)
