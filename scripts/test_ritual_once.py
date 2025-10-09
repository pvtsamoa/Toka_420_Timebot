"""
Run each ritual exactly once (now) without adding commands or starting polling.

Usage (defaults shown):
  TOKA_HUB_NAME="Los Angeles" TOKA_HUB_TZ="America/Los_Angeles" \
  python scripts/test_ritual_once.py

Env you can set before running:
  TOKA_HUB_NAME      e.g. "Los Angeles"
  TOKA_HUB_TZ        e.g. "America/Los_Angeles"
  TOKA_FALLBACK_CHAT_ID   chat id to receive messages (if /setchat not used)
Notes:
  - Requires TELEGRAM_BOT_TOKEN in your .env (already in config.py).
  - Uses your per-chat settings: /token, /lang, /moon (from data/chat_state.json).
"""
import os, asyncio
from dotenv import load_dotenv

# PTB v20+
from telegram.ext import Application

# Our one-shot helpers from scheduler
from scheduler.jobs import run_pre_roll_once, run_holy_minute_once

def _env(name: str, default: str) -> str:
    v = os.getenv(name, "").strip()
    return v if v else default

async def main() -> None:
    load_dotenv()  # pull TELEGRAM_BOT_TOKEN, etc.
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment (.env)")

    # Hub to test
    hub_name = _env("TOKA_HUB_NAME", "Los Angeles")
    hub_tz   = _env("TOKA_HUB_TZ",   "America/Los_Angeles")

    # If you haven’t used /setchat, set this before running:
    #   export TOKA_FALLBACK_CHAT_ID="-1001234567890"
    # (We do NOT set it here to avoid surprises; your env decides.)

    app = Application.builder().token(token).build()
    # We are not polling; we just need the bot initialized for send_message
    await app.initialize()

    print(f"➡️  Sending Pre-Roll once to hub: {hub_name} ({hub_tz}) …")
    await run_pre_roll_once(app, hub_name, hub_tz)

    print(f"➡️  Sending Holy Minute once to hub: {hub_name} ({hub_tz}) …")
    await run_holy_minute_once(app, hub_name, hub_tz)

    await app.shutdown()
    print("✅ Done. Check your Telegram chat for two messages.")

if __name__ == "__main__":
    asyncio.run(main())
