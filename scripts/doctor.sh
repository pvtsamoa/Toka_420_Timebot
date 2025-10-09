#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."
. .venv/bin/activate
python - <<'PY'
import importlib, py_compile, sys
ok = True
def check(path):
    global ok
    try:
        py_compile.compile(path, doraise=True)
        print(f"✓ compiled: {path}")
    except Exception as e:
        ok = False
        print(f"✗ {path}: {e}")

for f in ("app.py","scheduler/jobs.py","services/render.py","commands/news.py","commands/token.py"):
    try: check(f)
    except Exception as e: print(e)

# import hot spots
for mod in ("scheduler.jobs","commands.news","commands.token","commands.status"):
    try:
        importlib.import_module(mod)
        print(f"✓ import: {mod}")
    except Exception as e:
        ok = False
        print(f"✗ import {mod}: {e}")

print("Doctor:", "ALL GOOD" if ok else "ISSUES FOUND")
sys.exit(0 if ok else 1)
PY
