import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get or set the current crypto token for price queries."""
    if not context.args:
        cur = context.bot_data.get("token_override")
        await update.message.reply_text(f"Current token: {cur or 'DEFAULT (Weedcoin)'}")
        return
    
    new_token = context.args[0].strip()
    
    # Input validation
    if not new_token:
        await update.message.reply_text("❌ Token cannot be empty")
        return
    
    if len(new_token) > 100:
        await update.message.reply_text("❌ Token too long (max 100 chars)")
        return
    
    if not all(c.isalnum() or c in "-_" for c in new_token):
        await update.message.reply_text("❌ Invalid token format. Use alphanumeric, dash, or underscore only")
        return
    
    context.bot_data["token_override"] = new_token
    logger.info(f"Token set to: {new_token} (user: {update.effective_user.id})")
    await update.message.reply_text(f"✅ Token set for this session: {new_token}")


async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Health check endpoint to verify bot is running."""
    logger.info(f"Health check requested by user {update.effective_user.id}")
    await update.message.reply_text("🟢 Toka is healthy and running ✨")
