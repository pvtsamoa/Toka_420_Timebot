from telegram import Update
from telegram.ext import ContextTypes
from services.price import get_anchor
from datetime import datetime
import pytz

def _fmt_usd(n: float) -> str:
    # keep small tokens readable (6 decimals), big ones normal (2)
    return f"${n:,.6f}" if n < 1 else f"${n:,.2f}"

async def token_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    q = " ".join(context.args).strip() or "Weedcoin"
    q_up = q.upper()

    anchor = get_anchor(q)
    if not anchor:
        await update.message.reply_text(f"⚠️ No anchor for {q_up} right now. Try again in a minute.")
        return

    price, pct, vol = anchor
    arrow = "↑" if pct >= 0 else "↓"
    now = datetime.now(tz=pytz.timezone("America/Los_Angeles")).strftime("%H:%M %Z")

    lines = []
    lines.append(f"🌿 4:20 Anchor — {q_up}")
    lines.append("────────────────")
    lines.append(f"Price: {_fmt_usd(price)}")
    lines.append(f"24h:   {pct:.2f}% {arrow}")
    lines.append(f"Vol24: {_fmt_usd(vol)}")
    lines.append("")
    lines.append(f"⏱ Updated: {now}")
    lines.append("🧭 Keep your canoe balanced. Bongterm > FOMO.")
    await update.message.reply_text("\n".join(lines))
