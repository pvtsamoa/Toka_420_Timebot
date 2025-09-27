from telegram import Update
from telegram.ext import ContextTypes
from scheduler.jobs import _xrelay

async def x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        state = "ON" if _xrelay.enabled else "OFF"
        await update.message.reply_text(f"X relay is currently {state}")
        return
    arg = context.args[0].lower()
    if arg in ["on","off"]:
        prev,new = _xrelay.toggle(arg=="on")
        await update.message.reply_text(f"X relay toggled {prev}->{new}")
