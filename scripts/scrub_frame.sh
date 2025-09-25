#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
OUT="scrubbed_frame_$(date -u +%Y%m%dT%H%M%SZ).txt"

mask() {
  sed -E \
    -e 's/([A-Za-z0-9_]*API[_A-Z]*KEY[A-Za-z0-9_]*=)[^[:space:]]+/\1[REDACTED]/g' \
    -e 's/(SECRET|TOKEN|PASSWORD|WEBHOOK|BEARER)=([^[:space:]]+)/\1=[REDACTED]/g' \
    -e 's/([0-9A-Za-z]{8})[0-9A-Za-z_-]{12,}([0-9A-Za-z]{4})/\1…\2/g'
}

{
  echo "=== DATE (UTC) ==="
  date -u
  echo

  echo "=== ENV (selected) ==="
  awk -F= '
    $1 ~ /^(TZ|DEFAULT_TOKEN|TELEGRAM_SCOPE|MAJOR_X_ZONES|TELEGRAM_GLOBAL_CHAT_ID|X_ENABLED|X_API_KEY|X_API_SECRET|X_ACCESS_TOKEN|X_ACCESS_SECRET|TELEGRAM_BOT_TOKEN|OPENAI_API_KEY)$/ {print}
  ' <(env) | mask
  echo

  echo "=== PROCESS TREE ==="
  ps -Af | grep -E 'python|tmux|curl|node' | grep -v grep
  echo

  echo "=== TMUX SESSIONS ==="
  tmux ls 2>/dev/null || true
  echo

  echo "=== CRONTAB ==="
  crontab -l 2>/dev/null || echo "(no crontab)"
  echo

  echo "=== Termux-services (if any) ==="
  sv-list 2>/dev/null || echo "(termux-services not installed)"
  echo

  echo "=== GIT STATUS ==="
  git rev-parse --short HEAD 2>/dev/null || true
  git status --porcelain 2>/dev/null || true
  echo

  echo "=== FILE MAP (top) ==="
  find . -maxdepth 2 -type f | sort
  echo

  echo "=== scripts/*.sh ==="
  for f in scripts/*.sh; do
    echo "--- $f ---"
    sed -n '1,200p' "$f" | mask
    echo
  done

  echo "=== app.py (imports & X calls) ==="
  grep -nE 'from services|post_to_x|requests\.post|statuses/update|/2/tweets' -n app.py || true
  echo

  echo "=== services/*.py (interesting lines) ==="
  for f in services/*.py; do
    echo "--- $f ---"
    grep -nE 'def post_to_x|get_x_state|requests\.post|webhook|zapier|make\.com|ifttt|n8n|discord|slack|statuses/update|/2/tweets' "$f" || true
    echo
  done

  echo "=== Search repo for webhook/bridges ==="
  grep -RInE 'webhook|zapier|ifttt|make\.com|n8n|tweetdeck|metricool|client\.create_tweet|/2/tweets|statuses/update|curl -X POST' -- . | sed -E 's/(https?:\/\/[^[:space:]]+)/[URL]/g' || true
  echo

  echo "=== LAST 500 LINES OF LOG ==="
  tail -n 500 logs/bot.log 2>/dev/null || echo "(no logs/bot.log)"
  echo

  echo "=== x_state.json ==="
  if [ -f data/x_state.json ]; then
    cat data/x_state.json | mask
  else
    echo "(no data/x_state.json)"
  fi
} > "$OUT"

echo "Wrote $OUT"
