from telegram import Update
from telegram.ext import ContextTypes
from services.news import sources_by_region
from scheduler.jobs import last_call_info, next_scheduled_summary, x_status

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lc = last_call_info()
    last_line = f"{lc[0]} — {lc[1]}" if lc else "none"
    nxt = next_scheduled_summary()
    srcs = ", ".join(sorted(set(sum((v for v in sources_by_region().values()), []))))
    xflag = "ON" if x_status() else "OFF"
    news_health=[]
    for src in NEWS_SOURCES:
        try:
            requests.get(f"https://{src.lower()}.com",timeout=3)
            news_health.append(f"✅ {src}")
        except:
            news_health.append(f"❌ {src}")
    health_line=\"News health: \"+\", \".join(news_health)
    from services.news import NEWS_SOURCES
    import requests
    msg = (
        "✅ Toka 420 TimeBot — status\n"
        f"Last call: {last_line}\n"
        f"Next: {nxt}\n"
        f"News sources: {srcs}\n"
        f"{health_line}\n" \
        f"X relay: {xflag}"
    )
    await update.message.reply_text(msg)
