#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$HOME/Toka_420_Timebot"
SESSION="toka420"
LOG="$ROOT/logs/bot.log"

mkdir -p "$ROOT/logs"

# stop any old session quietly
tmux has-session -t "$SESSION" 2>/dev/null && tmux kill-session -t "$SESSION" || true

cd "$ROOT"

# --- load .env into the environment (handles CRLF/BOM safely) ---
if [ -f .env ]; then
  # strip BOM + Windows CRLF, then source
  sed '1s/^\xEF\xBB\xBF//' .env | sed 's/\r$//' > .env.clean
  set -a
  . ./.env.clean
  set +a
  rm -f .env.clean
fi

# activate venv if present
[ -f "$ROOT/.venv/bin/activate" ] && . "$ROOT/.venv/bin/activate"

# log a quick header (mask most of the token)
MASKED_TOKEN="${TELEGRAM_BOT_TOKEN:-missing}"
[ "${#MASKED_TOKEN}" -gt 12 ] && MASKED_TOKEN="${MASKED_TOKEN:0:9}********"

{
  echo "--- $(date) starting Toka ---"
  echo "TELEGRAM_BOT_TOKEN: $MASKED_TOKEN"
  echo "CHAT_IDS: ${CHAT_IDS:-<none>}"
} >> "$LOG"

# run the bot inside tmux, piping output to the log
tmux new-session -d -s "$SESSION" "cd $ROOT && python app.py >> \"$LOG\" 2>&1"

echo "Started Toka in tmux session '$SESSION'."
echo "Logs: $LOG"
echo "View: tmux attach -t $SESSION"
