from __future__ import annotations
import os, random
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

POOL_DIR = Path(os.getenv("NEWS_POOL_DIR", "data/news"))

def _pick_one(region: str) -> str:
    path = POOL_DIR / f"{region.lower()}.txt"
    if not path.exists():
        return f"[no pool for {region}]"
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.lstrip().startswith("#")]
    return random.choice(lines) if lines else f"[pool empty: {region}]"

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply with one headline per region. Args = list of region names."""
    regions_env = os.getenv("NEWS_REGIONS", "Samoa,California,London")
    regions = context.args or [r.strip() for r in regions_env.split(",") if r.strip()]
    bits = [f"• {r}: {_pick_one(r)}" for r in regions]
    await update.message.reply_text("🗞️ Headlines\n" + "\n".join(bits))
