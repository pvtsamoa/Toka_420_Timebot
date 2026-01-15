import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from services.dexscreener import get_anchor

logger = logging.getLogger(__name__)


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show 1-day and 3-day price movement with liquidity for a token (default: Weedcoin)."""
    user_id = update.effective_user.id
    
    # Get token symbol from args or default
    token_symbol = None
    if context.args and context.args[0].strip():
        token_symbol = context.args[0].strip().lower()
        
        # Input validation
        if len(token_symbol) > 100:
            await update.message.reply_text("❌ Token too long (max 100 chars)")
            logger.warning(f"Token too long: {token_symbol} (user: {user_id})")
            return
        
        if not all(c.isalnum() or c in "-_" for c in token_symbol):
            await update.message.reply_text("❌ Invalid token format. Use alphanumeric, dash, or underscore only")
            logger.warning(f"Invalid token format: {token_symbol} (user: {user_id})")
            return
    else:
        # Default to Weedcoin
        token_symbol = os.getenv("DEFAULT_TOKEN", "weedcoin").lower()
    
    logger.info(f"Token price query for: {token_symbol} (user: {user_id})")
    
    try:
        # Fetch anchor data from DexScreener
        anchor = get_anchor(token_symbol)
        
        if not anchor:
            await update.message.reply_text(
                f"❌ Could not find token: `{token_symbol}`\n\n"
                f"Try `/token weedcoin` or `/token btc`",
                parse_mode="Markdown"
            )
            logger.warning(f"Token not found: {token_symbol}")
            return
        
        # Format response with price movement
        symbol = anchor.get("symbol", "?").upper()
        price = anchor.get("price", "?")
        change24 = anchor.get("change24", "±0.00%")
        vol24 = anchor.get("vol24", "$0")
        dex = anchor.get("dex", "").upper()
        
        # Build message
        message = f"""
💰 **{symbol}** Price Chart

🔢 **Current Price**
`{price}`

📈 **24h Movement**
{change24}

💧 **24h Liquidity**
{vol24}

🏪 **Exchange**: {dex}

────────────────────
*Try `/token` again for fresh data*
*Use `/news` for market updates*
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ Sent price data for {symbol} (user: {user_id})")
        
    except Exception as e:
        logger.exception(f"Error fetching token data for {token_symbol}: {e}")
        await update.message.reply_text(
            f"⚠️ Error fetching price data. Try again later.",
            parse_mode="Markdown"
        )


async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Health check endpoint to verify bot is running."""
    logger.info(f"Health check requested by user {update.effective_user.id}")
    await update.message.reply_text("🟢 Toka is healthy and running ✨")
