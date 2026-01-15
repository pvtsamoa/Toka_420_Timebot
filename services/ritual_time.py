import os
import random
import logging
from services.ritual import build_ritual_text, load_media_bank
from services.dexscreener import get_anchor

logger = logging.getLogger(__name__)

def _pick_tip():
    """Pick a random safety tip or proverb."""
    try:
        bank = load_media_bank()
        tips = (bank.get("safety") or []) + (bank.get("proverbs") or [])
        return random.choice(tips) if tips else "Shield up: keep seed phrases dry; ignore DM links."
    except Exception as e:
        logger.exception(f"Failed to pick tip: {e}")
        return "Shield up: keep seed phrases dry; ignore DM links."

async def ritual_call(context):
    """Execute the 4:20 ritual for a hub."""
    hub_name = context.job.name.replace("420_", "")
    token = context.bot_data.get("token_override") or os.getenv("DEFAULT_TOKEN", "weedcoin")
    chat_id = os.getenv("TELEGRAM_GLOBAL_CHAT_ID")
    
    try:
        # Validate configuration
        if not chat_id:
            logger.error(f"❌ TELEGRAM_GLOBAL_CHAT_ID not set! Cannot send ritual for {hub_name}")
            return
        
        logger.info(f"🌊 Starting ritual for {hub_name} with token={token}")
        
        # Build ritual message
        text = build_ritual_text(hub_name, token)
        
        # Send to Telegram
        await context.bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"✅ Ritual sent successfully for {hub_name}")
        
    except Exception as e:
        logger.exception(f"💥 Ritual failed for {hub_name}: {e}")
