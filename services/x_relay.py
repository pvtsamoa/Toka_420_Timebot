from __future__ import annotations
import os, json, time, math
from pathlib import Path
import requests
from typing import Optional

LOG = Path("data/x_relay.log")
POST_URL = "https://api.twitter.com/2/tweets"

def _log(line: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    LOG.open("a", encoding="utf-8").write(f"[{ts}] {line}\n")

def _bearer() -> Optional[str]:
    # Allow either name; user-context OAuth2 bearer is required for write.
    return os.environ.get("X_BEARER") or os.environ.get("X_TOKEN")

def relay_enabled() -> bool:
    # Feature flag + credentials presence
    from services.x_state import is_on
    return bool(is_on() and _bearer())

def post_text(text: str) -> bool:
    """
    Non-blocking philosophy: if relay disabled or creds missing, we log & return False.
    Returns True only on 2xx response from X.
    """
    if not _bearer():
        _log("SKIP: no X_BEARER/X_TOKEN set.")
        return False
    if not text or not text.strip():
        _log("SKIP: empty text.")
        return False

    headers = {
        "Authorization": f"Bearer {_bearer()}",
        "Content-Type": "application/json",
    }
    payload = {"text": text[:274]}  # safety trim; X hard limit 280 (reserve a few)
    try:
        r = requests.post(POST_URL, headers=headers, json=payload, timeout=10)
        if 200 <= r.status_code < 300:
            _log(f"OK: posted tweet id={getattr(r.json(), 'id', '?')} text={payload['text']!r}")
            return True
        _log(f"ERR {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        _log(f"EXC: {e}")
        return False

def post_with_backoff(text: str, retries: int = 1) -> bool:
    """
    Try to post once; if fail and retries>0, sleep and retry.
    Never raises — only logs. Returns True if one attempt succeeded.
    """
    if not relay_enabled():
        _log("SKIP: relay disabled.")
        return False
    ok = post_text(text)
    if ok or retries <= 0:
        return ok
    # simple backoff: 3s then 6s...
    for i in range(1, retries + 1):
        time.sleep(3 * i)
        if post_text(text):
            return True
    return False
