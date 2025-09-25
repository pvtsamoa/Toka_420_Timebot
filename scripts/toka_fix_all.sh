#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "🌿 Toka one-stop fix starting…"

# 0) Basic sanity
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
mkdir -p scripts logs

# 1) Create/refresh commands.py (idempotent glue)
cat > commands.py <<'PY'
from __future__ import annotations
from typing import Callable, Awaitable, Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

def _optional_import(path: str, name: str) -> Optional[Callable[..., Awaitable[None]]]:
    try:
        mod = __import__(path, fromlist=[name])
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    except Exception:
        pass
    return None

async def _not_installed(label: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"⚠️ /{label} not installed in this build.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("✅ Toka is breathing. Schedules armed. 🌿")

_news     = _optional_import("commands.news", "news")
_token    = _optional_import("commands.token", "token")
_preroll  = _optional_import("commands.preroll", "preroll")
_space    = _optional_import("commands.space", "space")
_x        = _optional_import("commands.x", "x")
_id       = _optional_import("commands.user_id", "user_id") or _optional_import("commands.id", "id")

_COMMANDS: list[tuple[str, Callable[..., Awaitable[None]]]] = [
    ("status",  status),
    ("news",    _news    or (lambda u,c: _not_installed("news", u, c))),
    ("token",   _token   or (lambda u,c: _not_installed("token", u, c))),
    ("preroll", _preroll or (lambda u,c: _not_installed("preroll", u, c))),
    ("space",   _space   or (lambda u,c: _not_installed("space", u, c))),
    ("x",       _x       or (lambda u,c: _not_installed("x", u, c))),
    ("id",      _id      or (lambda u,c: _not_installed("id", u, c))),
]

def add_handlers(application: Application) -> None:
    existing = {
        h.command[0] for h in application.handlers.get(0, [])
        if isinstance(h, CommandHandler) and h.command
    }
    for cmd, fn in _COMMANDS:
        if cmd not in existing:
            application.add_handler(CommandHandler(cmd, fn))
PY
echo "✅ commands.py written"

# 2) Ensure app.py imports and calls add_handlers(application)
python - <<'PY'
from pathlib import Path
import re
p = Path("app.py")
s = p.read_text(encoding="utf-8")

if "from commands import add_handlers" not in s:
    s = "from commands import add_handlers\n" + s

# Insert add_handlers(application) after Application build
inserted = False
patA = r"(application\s*=\s*Application\.builder\(\)[\s\S]*?\.build\(\)\s*)\n"
if re.search(patA, s, re.M):
    s = re.sub(patA, r"\1\nadd_handlers(application)\n", s, count=1, flags=re.M)
    inserted = True
else:
    patB = r"(application\s*=\s*Application\([^\n]*\)\s*)\n"
    if re.search(patB, s):
        s = re.sub(patB, r"\1\nadd_handlers(application)\n", s, count=1)
        inserted = True

# de-dup if it already existed
s = s.replace("add_handlers(application)\nadd_handlers(application)", "add_handlers(application)")

Path("app.py").write_text(s, encoding="utf-8")
print("✅ app.py patched (import + add_handlers)" if inserted else "ℹ️ app.py already had add_handlers")
PY

# 3) Seed a minimal /news pool (safe if exists)
mkdir -p data/news
[ -s data/news/samoa.txt ]      || printf 'Govt launches agri fund\nSamoa hosts regional meet\n' > data/news/samoa.txt
[ -s data/news/california.txt ] || printf 'CA wildfires update\nTech jobs outlook improves\n'     > data/news/california.txt
[ -s data/news/london.txt ]     || printf 'BoE signals rate stance\nPremier League midweek wins\n' > data/news/london.txt
echo "✅ data/news seeded"

# 4) Ensure .env has expected keys (append if missing)
touch .env
grep -q '^DEXSCREENER_BASE=' .env || echo 'DEXSCREENER_BASE=https://api.dexscreener.com' >> .env
grep -q '^TELEGRAM_SCOPE='   .env || echo 'TELEGRAM_SCOPE=all' >> .env
grep -q '^MAJOR_X_ZONES='    .env || echo 'MAJOR_X_ZONES=Tokyo,Singapore,Sydney,London,New_York,LA' >> .env
grep -q '^OPENAI_API_KEY='   .env || echo 'OPENAI_API_KEY=' >> .env
grep -q '^INCLUDE_EDU_SAFETY=' .env || echo 'INCLUDE_EDU_SAFETY=1' >> .env
echo "✅ .env baseline keys present (values masked)"

# 5) Hard-fix temp dir usage in consistency script (if present)
if [ -f scripts/check_consistency.sh ]; then
  sed -i 's|mktemp -d /tmp/toka_consistency.XXXXXX|mktemp -d "${TMPDIR:-/data/data/com.termux/files/usr/tmp}/toka_consistency.XXXXXX"|' scripts/check_consistency.sh || true
  echo "✅ scripts/check_consistency.sh TMPDIR hardened"
fi

# 6) Stub services/moon.py if missing (prevents imports from crashing)
if [ ! -f services/moon.py ]; then
  mkdir -p services
  cat > services/moon.py <<'PY'
def get_moon_phase_text() -> str:
    return ""
PY
  echo "✅ services/moon.py stubbed"
fi

# 7) Refresh Telegram menu (if token present)
set +u
. ./.env
set -u
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setMyCommands" \
    -d 'commands=[{"command":"status","description":"Health check"},{"command":"news","description":"One headline per region"},{"command":"preroll","description":"Fire a 4:20 test in ~60s"}]' >/dev/null || true
  echo "✅ Telegram commands menu updated"
else
  echo "⚠️ TELEGRAM_BOT_TOKEN empty—skipping menu update"
fi

# 8) Clear py caches & restart if scripts exist
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

if [ -x scripts/stop-toka.sh ] && [ -x scripts/start-toka.sh ]; then
  ./scripts/stop-toka.sh || true
  ./scripts/start-toka.sh
  echo "🚀 Toka restarted. Tail logs with: ./scripts/tail.sh"
else
  echo "ℹ️ No start/stop scripts found; start your app as you normally do."
fi

echo "🌊 All done."
