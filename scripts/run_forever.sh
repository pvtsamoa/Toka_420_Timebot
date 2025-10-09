#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
mkdir -p logs
# keep device awake (Termux)
termux-wake-lock >/dev/null 2>&1 || true
# rotate log (simple)
[ -f logs/bot.log ] && mv logs/bot.log "logs/bot.$(date +%Y%m%d-%H%M%S).log"
# run in a tmux session named 'toka'
if ! tmux has-session -t toka 2>/dev/null; then
  tmux new-session -ds toka "python app.py 2>&1 | tee logs/bot.log"
else
  echo "tmux session 'toka' already running."
fi
echo "✓ Toka running in tmux. Attach: tmux attach -t toka   |   Detach: Ctrl-b d"
