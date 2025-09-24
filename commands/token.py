async def token(update, context):
    if not context.args:
        cur = context.bot_data.get("token_override")
        await update.message.reply_text(f"Current token: {cur or 'DEFAULT'}"); return
    new = context.args[0].strip(); context.bot_data["token_override"] = new
    await update.message.reply_text(f"✅ Token set for this run: {new}")
