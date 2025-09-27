from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import _xrelay  # uses the singleton created in scheduler

async def x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # No args: report current state
    if not context.args:
        state = "ON" if _xrelay.enabled else "OFF"
        await update.message.reply_text(f"🚣 X relay is currently {state}")
        return

    arg = (context.args[0] or "").lower()
    if arg not in ("on", "off"):
        await update.message.reply_text("Usage: /x on | /x off")
        return

    prev, new = _xrelay.toggle(arg == "on")
    await update.message.reply_text(
        f"🚣 X relay toggled {(ON if prev else OFF)} → {(ON if new else OFF)}"
    )
