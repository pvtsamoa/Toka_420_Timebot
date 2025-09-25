#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$REPO_ROOT" ]; then
  echo "❌ Not a git repo. cd into your Toka_420_Timebot clone and retry."
  exit 1
fi
cd "$REPO_ROOT"

mkdir -p logs /tmp
REPORT="logs/consistency_report_$(date +%Y%m%d_%H%M%S).txt"

echo "⏱ $(date)" | tee "$REPORT"
echo "📂 Repo root: $REPO_ROOT" | tee -a "$REPORT"
echo "🔗 Remotes:" | tee -a "$REPORT"
git remote -v | tee -a "$REPORT"

# Detect upstream branch (default to origin/main)
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo origin/main)"
echo "🌿 Upstream: $UPSTREAM" | tee -a "$REPORT"

echo "🛰  Fetching latest..." | tee -a "$REPORT"
git fetch --all --prune >> "$REPORT" 2>&1 || true

echo "🧮 Ahead/Behind vs $UPSTREAM:" | tee -a "$REPORT"
git rev-list --left-right --count "$UPSTREAM"...HEAD | awk '{print "behind/ahead:",$1,$2}' | tee -a "$REPORT"

echo "📝 Local changes vs $UPSTREAM (name-status):" | tee -a "$REPORT"
git diff --name-status "$UPSTREAM"...HEAD | tee -a "$REPORT"

echo "📦 Untracked files (not in git):" | tee -a "$REPORT"
git ls-files --others --exclude-standard | tee -a "$REPORT"

echo "🙈 Ignored files (top level):" | tee -a "$REPORT"
git status --ignored -s | tee -a "$REPORT"

# Required files for Toka 420 TimeBot (from your v3.x structure)
REQ_FILES=(
  "app.py"
  "scheduler.py"
  "commands.py"
  "services/dexscreener.py"
  "services/news.py"
  "services/moon.py"
  ".env"
)
echo "🔎 Verifying required files exist:" | tee -a "$REPORT"
for f in "${REQ_FILES[@]}"; do
  if [ -e "$f" ]; then echo "  ✅ $f" | tee -a "$REPORT"; else echo "  ❌ $f MISSING" | tee -a "$REPORT"; fi
done

# .env key presence check (mask values)
ENV_KEYS=( "TELEGRAM_BOT_TOKEN" "DEXSCREENER_BASE" "TELEGRAM_SCOPE" "MAJOR_X_ZONES" "OPENAI_API_KEY" )
echo "🔐 .env keys present (values masked):" | tee -a "$REPORT"
if [ -f ".env" ]; then
  while IFS= read -r key; do
    val="$(grep -E "^$key=" .env | head -n1 || true)"
    if [ -n "$val" ]; then echo "  ✅ $key=******" | tee -a "$REPORT"; else echo "  ❌ $key MISSING" | tee -a "$REPORT"; fi
  done < <(printf "%s\n" "${ENV_KEYS[@]}")
else
  echo "  ❌ .env not found" | tee -a "$REPORT"
fi

# Hash compare with a fresh temp clone AT THE SAME REVISION as upstream
TMPDIR="$(mktemp -d "${TMPDIR:-/data/data/com.termux/files/usr/tmp}/toka_consistency.XXXXXX")"
echo "🧪 Creating temp clone for hash compare: $TMPDIR" | tee -a "$REPORT"

ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$ORIGIN_URL" ]; then
  echo "❌ No 'origin' remote found. Skipping hash compare." | tee -a "$REPORT"
else
  git clone --quiet "$ORIGIN_URL" "$TMPDIR/src"
  ( cd "$TMPDIR/src" && git checkout --quiet "$(echo "$UPSTREAM" | awk -F/ '{print $2}')" )

  # Make normalized file lists (exclude common noisy dirs)
  EXCLUDES='(^\.git/|^\.venv/|^__pycache__/|^logs/|^data/|^backups/|^\.mypy_cache/|\.pyc$)'
  find . -type f | sed 's|^\./||' | grep -Ev "$EXCLUDES" | sort > "$TMPDIR/local_files.txt"
  ( cd "$TMPDIR/src" && find . -type f | sed 's|^\./||' | grep -Ev "$EXCLUDES" | sort ) > "$TMPDIR/remote_files.txt"

  echo "📄 File set differences (local vs remote):" | tee -a "$REPORT"
  comm -3 "$TMPDIR/local_files.txt" "$TMPDIR/remote_files.txt" | sed 's/^\t/REMOTE ONLY: /; s/^/LOCAL ONLY: /' | tee -a "$REPORT"

  echo "🔐 SHA256 diffs (files present in both):" | tee -a "$REPORT"
  join "$TMPDIR/local_files.txt" "$TMPDIR/remote_files.txt" | while read -r path; do
    lsum="$(sha256sum "$path" | awk '{print $1}')" || lsum="ERR"
    rsum="$(sha256sum "$TMPDIR/src/$path" | awk '{print $1}')" || rsum="ERR"
    [ "$lsum" = "$rsum" ] || printf "  ❗ %s\n      LOCAL : %s\n      REMOTE: %s\n" "$path" "$lsum" "$rsum"
  done | tee -a "$REPORT"
fi

echo "✅ Report saved to: $REPORT"
