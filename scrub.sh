#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "== Toka total scrub starting =="

cd ~/Toka_420_Timebot

# 1) Stop tmux session if running
tmux has-session -t toka420 2>/dev/null && tmux kill-session -t toka420 || true

# 2) Backup current tree (skip venv and git)
ts="$(date +%Y%m%d_%H%M%S)"
tar --exclude='.venv' --exclude='.git' -czf "full_backup_${ts}.tgz" . || true
echo "Backup: full_backup_${ts}.tgz"

# 3) Normalize terminology across repo (safe, idempotent)
#    - TELEGRAM_BOT_TOKEN -> TELEGRAM_BOT_TOKEN
#    - 'app.' -> 'application.'
#    - 'return app' -> 'return application'
#    - ticker/hashtag/tag for X relay
find . -type f ! -path "./.git/*" ! -path "./.venv/*" \
  -exec sed -i 's/TELEGRAM_BOT_TOKEN/TELEGRAM_BOT_TOKEN/g' {} + || true

grep -RIl '(^|[^a-zA-Z0-9_])app\.' . 2>/dev/null | xargs -r sed -i 's/\bapp\./application./g'
grep -RIl 'return app\b' . 2>/dev/null | xargs -r sed -i 's/return app/return application/g'

# X relay standardization (ticker/hashtag/handle)
grep -RIl '\$WEEDCOIN' services 2>/dev/null | xargs -r sed -i 's/\$WEEDCOIN/\$weedcoin/g'
grep -RIl '#weedcoin' services README.md 2>/dev/null | xargs -r sed -i 's/#weedcoin/#Weedcoin/g'
# Ensure handle referenced where applicable (runtime enforces already; no global force here)

# 4) Clean app.py to a minimal, known-good version
cat > app.py <<'PY'
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from commands.status import status
from commands.token import token
try:
    from commands.preroll import preroll
    HAS_PREROLL = True
except Exception:
    HAS_PREROLL = False

from scheduler import schedule_hubs
from services.ritual_time import ritual_call

def build_app():
    load_dotenv(override=True)

    application = Application.builder().token(
        os.getenv("TELEGRAM_BOT_TOKEN")
    ).build()

    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("token", token))
    if HAS_PREROLL:
        application.add_handler(CommandHandler("preroll", preroll))

    schedule_hubs(application.job_queue, ritual_call)
    return application

if __name__ == "__main__":
    build_app().run_polling(drop_pending_updates=True)
PY

# 5) Ensure /preroll exists (create a clean one if missing)
if [ ! -f commands/preroll.py ]; then
  mkdir -p commands
  cat > commands/preroll.py <<'PY'
import os, datetime as dt
import pytz
from services.ritual_time import ritual_call

def _tz():
    name = os.getenv("TZ", "UTC")
    try:
        return pytz.timezone(name)
    except Exception:
        return pytz.UTC

def _next_3am(tz):
    now = dt.datetime.now(tz)
    target = tz.localize(dt.datetime(now.year, now.month, now.day, 3, 0, 0))
    if now >= target:
        target = target + dt.timedelta(days=1)
    return target

async def preroll(update, context):
    tz = _tz()
    when_local = _next_3am(tz)
    when_utc = when_local.astimezone(pytz.UTC)
    context.application.job_queue.run_once(
        ritual_call, when=when_utc, name="420_PREROLL"
    )
    await update.message.reply_text(
        f"🧪 Preroll scheduled for {when_local.strftime('%Y-%m-%d %H:%M')} {tz.zone} "
        f"({when_utc.strftime('%H:%M')} UTC)."
    )
PY
fi

# 6) Replace start script with clean version (prints masked token & chat id)
mkdir -p scripts logs
cat > scripts/start-toka.sh <<'BASH'
#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd ~/Toka_420_Timebot

# load env + venv
[ -f .env ] && set -a && . ./.env && set +a || true
[ -f .venv/bin/activate ] && . .venv/bin/activate || true

TOK="${TELEGRAM_BOT_TOKEN:-missing}"
CID="${TELEGRAM_GLOBAL_CHAT_ID:-<none>}"
MASKED="$(printf '%s' "$TOK" | sed -E 's/^(.{9}).*/\1********/')"

echo "--- $(date -u) starting Toka ---"
echo "TELEGRAM_BOT_TOKEN: $MASKED"
echo "CHAT_ID: $CID"

tmux has-session -t toka420 2>/dev/null && tmux kill-session -t toka420 || true
tmux new-session -d -s toka420 "python app.py >> logs/bot.log 2>&1"
echo "Started Toka in tmux session 'toka420'."
echo "Logs: $(pwd)/logs/bot.log"
echo "View: tmux attach -t toka420"
BASH
chmod +x scripts/start-toka.sh

# 7) Purge caches & logs
find . -type d -name "__pycache__" -exec rm -rf {} + || true
find . -type f -name "*.pyc" -delete || true
: > logs/bot.log || true

# 8) Recreate venv and (re)install deps
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip wheel
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  pip install python-telegram-bot==21.* python-dotenv pytz httpx
fi

# 9) Sanity check token via Bot API /getMe
if [ -f .env ]; then set -a; . ./.env; set +a; fi
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "Validating TELEGRAM_BOT_TOKEN with /getMe ..."
  set +e
  RES="$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")"
  echo "$RES" | grep -q '"ok":true'
  OK=$?
  set -e
  if [ "$OK" -ne 0 ]; then
    echo "⚠️  /getMe failed. Check TELEGRAM_BOT_TOKEN in .env"
    echo "Raw: $RES"
    exit 1
  fi
else
  echo "⚠️  TELEGRAM_BOT_TOKEN missing in .env"
  exit 1
fi

# 10) Quick syntax check
python -m py_compile app.py

# 11) Start
./scripts/start-toka.sh

echo "== Toka total scrub complete =="
