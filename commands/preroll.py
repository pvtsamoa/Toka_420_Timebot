from datetime import timedelta
from services.ritual_time import ritual_call

async def preroll(update, context):
    # Fire once ~60s from now (JobQueue supports timedelta delays directly)
    delay = timedelta(seconds=60)
    context.application.job_queue.run_once(ritual_call, when=delay, name="420_PREROLL")
    await update.message.reply_text("🧪 Preroll set: will post in ~60 seconds.")
