from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json

DATA = Path("data/state/schedule.json")

def _load() -> dict:
    if not DATA.exists():
        return {}
    try:
        return json.loads(DATA.read_text(encoding="utf-8") or "{}")
    except Exception:
        return {}

def _save(d: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def mark_last_posted(kind: str, when: datetime | None = None) -> None:
    d = _load()
    when = when or datetime.now(timezone.utc)
    row = d.get(kind, {})
    row["last_posted_utc"] = when.isoformat()
    d[kind] = row
    _save(d)

def set_next_run(kind: str, when: datetime | None) -> None:
    d = _load()
    row = d.get(kind, {})
    row["next_run_utc"] = when.isoformat() if when else None
    d[kind] = row
    _save(d)

def get_status(kind: str) -> dict:
    d = _load().get(kind, {})
    return {
        "last_posted_utc": d.get("last_posted_utc"),
        "next_run_utc": d.get("next_run_utc"),
    }
