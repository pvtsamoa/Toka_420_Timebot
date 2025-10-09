from telegram import Update
from telegram.ext import ContextTypes
from services.x_state import toggle, is_on

async def x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hidden dev command; not documented in menu
    args = (context.args or [])
    if args and args[0].lower() in ("on","off"):
        flag = (args[0].lower() == "on")
        toggle(flag)
    else:
        toggle()  # flip
    await update.message.reply_text(f"X relay: {'ON' if is_on() else 'OFF'}")
