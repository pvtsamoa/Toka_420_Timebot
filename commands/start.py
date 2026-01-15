"""
/start command — Welcome and command reference
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with full command reference."""
    user_id = update.effective_user.id
    logger.info(f"Start command requested (user: {user_id})")
    
    message = """
🌿⛵️ **Toka 420 Time Bot** — Welcome, Navigator ✨

Your guide through cannabis culture & cryptocurrency. Every day at 4:20, Toka delivers rituals, wisdom, and price anchors across time zones.

────────────────────────

**📋 COMMANDS**

🟢 **/status**
Bot health, scheduler status, last price update, next 4:20 alert

📰 **/news**
Rotating market news (crypto → finance)
*Cycles through different news sources on each call*

🩺 **/health**
Quick bot health check

────────────────────────

**⏰ AUTOMATED RITUALS**

4:20 AM/PM (UTC) — Daily rituals across global hubs:
• Price anchor (Weedcoin & featured token)
• Navigator's Blessing (rotating wisdom)
• Safety reminder

────────────────────────

**💡 TIPS**

→ Use `/token weedcoin` regularly to track price movement
→ Check `/status` to confirm bot is active & schedule next alert
→ `/news apac` for Asia-Pacific market updates
→ Rituals fire **24/7** across all time zones

────────────────────────

*Questions? Check logs or ping the dev team.*

🌺 Navigator's blessing guide you through the markets ✨
"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
