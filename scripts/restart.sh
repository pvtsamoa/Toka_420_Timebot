#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
. .venv/bin/activate
tmux kill-session -t toka 2>/dev/null || true
bash scripts/run_forever.sh
