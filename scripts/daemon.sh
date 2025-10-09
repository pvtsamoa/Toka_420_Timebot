#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"
PY="$VENV/bin/python"
APP="$ROOT/app.py"
PIDFILE="$ROOT/logs/bot.pid"
LOGFILE="$ROOT/logs/bot.log"

# Load venv if present
[ -f "$VENV/bin/activate" ] && . "$VENV/bin/activate"

mkdir -p "$(dirname "$PIDFILE")" "$(dirname "$LOGFILE")"

start() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Already running (PID $(cat "$PIDFILE"))."
    exit 0
  fi
  echo "Starting bot in background..."
  [ -f "$LOGFILE" ] && mv "$LOGFILE" "$LOGFILE.$(date +%Y%m%d-%H%M%S)"
  nohup "$PY" "$APP" >>"$LOGFILE" 2>&1 &
  echo $! > "$PIDFILE"
  disown || true
  echo "✅ Started (PID $(cat "$PIDFILE")). Logs: $LOGFILE"
}

stop() {
  if [ -f "$PIDFILE" ]; then
    PID="$(cat "$PIDFILE")"
    if kill -0 "$PID" 2>/dev/null; then
      echo "Stopping PID $PID ..."
      kill "$PID" || true
      for i in 1 2 3 4 5; do
        kill -0 "$PID" 2>/dev/null || break
        sleep 1
      done
      kill -9 "$PID" 2>/dev/null || true
    else
      echo "Stale pidfile (no such PID)."
    fi
    rm -f "$PIDFILE"
    echo "🛑 Stopped."
  else
    echo "No pidfile; trying best-effort stop…"
    # stop any orphaned app.py from this venv
    if pgrep -f "$PY $APP" >/dev/null 2>&1; then
      pgrep -f "$PY $APP" | xargs -r kill
      sleep 1
      pgrep -f "$PY $APP" | xargs -r kill -9 || true
      echo "🛑 Stopped orphan run."
    else
      echo "Not running."
    fi
  fi
}

status() {
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Running (PID $(cat "$PIDFILE")). Log: $LOGFILE"
  else
    if pgrep -f "$PY $APP" >/dev/null 2>&1; then
      echo "Running (no pidfile). PIDs: $(pgrep -f "$PY $APP" | xargs echo)."
    else
      echo "Not running."
    fi
  fi
}

logs() {
  [ -f "$LOGFILE" ] || { echo "No log file yet: $LOGFILE"; exit 1; }
  echo "Tailing logs — Ctrl+C to stop."
  tail -n 200 -f "$LOGFILE"
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  logs) logs ;;
  *) echo "Usage: scripts/daemon.sh {start|stop|status|logs}"; exit 1 ;;
esac
