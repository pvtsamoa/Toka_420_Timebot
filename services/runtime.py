"""
services/runtime.py
-------------------
Runtime helpers for Toka:
- X (Twitter) relay with OAuth 1.0a to v1.1 statuses/update.json
- Last relay attempt state persistence for /status

Environment (.env):
  X_ENABLED=1
  # Either legacy or new naming is supported:
  #   Legacy: X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
  #     New: X_API_KEY,      X_API_SECRET,      X_ACCESS_TOKEN, X_ACCESS_SECRET

This module avoids external dotenv deps by lazy-loading .env once.
"""

from __future__ import annotations

import os
import json
import time
import hmac
import base64
import hashlib
import logging
from typing import Dict, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

# ------------------------------------------------------------------------------
# Basic config / paths
# ------------------------------------------------------------------------------

DATA_DIR = Path("data")            # relative to project root (works when app runs from root)
STATE_FILE = DATA_DIR / "x_state.json"

__all__ = ["post_to_x", "get_x_state", "record_x_attempt"]

# ------------------------------------------------------------------------------
# Lightweight .env loader (no dependency on python-dotenv)
# ------------------------------------------------------------------------------

def _load_env_once() -> None:
    if getattr(_load_env_once, "_did", False):
        return
    _load_env_once._did = True  # type: ignore[attr-defined]
    env_path = Path(".env")
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            # do not overwrite already-set environment
            os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        # Non-fatal; just continue with existing os.environ
        pass

# ------------------------------------------------------------------------------
# X relay state (for /status)
# ------------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _ensure_data_dir() -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def _read_state() -> Dict[str, Any]:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _write_state(st: Dict[str, Any]) -> None:
    _ensure_data_dir()
    try:
        STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logging.warning("Could not write x_state.json: %s", e)

def record_x_attempt(ok: bool, error: str | None = None, text: str | None = None) -> None:
    st = _read_state()
    st["last_attempt_iso"] = _now_iso()
    st["last_status"] = "ok" if ok else "error"
    st["last_error"] = error or ""
    if text is not None:
        st["last_text"] = text
    _write_state(st)

def get_x_state() -> Dict[str, Any]:
    return _read_state()

# ------------------------------------------------------------------------------
# OAuth 1.0a helpers
# ------------------------------------------------------------------------------

def _pct(x: Any) -> str:
    """RFC 3986 percent-encoding with the OAuth 'safe' set."""
    return quote(str(x), safe="~-._")

def _gather_creds() -> Tuple[bool, str, str, str, str]:
    """
    Returns (ok, consumer_key, consumer_secret, access_token, access_token_secret).
    Accepts both naming schemes; prefers legacy if both present.
    """
    _load_env_once()
    ck  = os.getenv("X_CONSUMER_KEY") or os.getenv("X_API_KEY") or ""
    cs  = os.getenv("X_CONSUMER_SECRET") or os.getenv("X_API_SECRET") or ""
    at  = os.getenv("X_ACCESS_TOKEN") or ""
    ats = os.getenv("X_ACCESS_TOKEN_SECRET") or os.getenv("X_ACCESS_SECRET") or ""

    missing = []
    if not ck:  missing.append("X_CONSUMER_KEY/X_API_KEY")
    if not cs:  missing.append("X_CONSUMER_SECRET/X_API_SECRET")
    if not at:  missing.append("X_ACCESS_TOKEN")
    if not ats: missing.append("X_ACCESS_TOKEN_SECRET/X_ACCESS_SECRET")
    if missing:
        return False, "", "", "", ""

    return True, ck, cs, at, ats

def _oauth1_header(method: str, url: str, body_params: Dict[str, Any],
                   ck: str, cs: str, at: str, ats: str) -> str:
    """
    Build OAuth 1.0a Authorization header for application/x-www-form-urlencoded body.
    """
    oauth_params = {
        "oauth_consumer_key": ck,
        "oauth_nonce": base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip("="),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": at,
        "oauth_version": "1.0",
    }
    # Params included in signature: OAuth + body
    all_params = {**oauth_params, **body_params}
    param_str = "&".join(f"{_pct(k)}={_pct(all_params[k])}" for k in sorted(all_params))
    base_string = "&".join((_pct(method.upper()), _pct(url), _pct(param_str)))

    signing_key = f"{_pct(cs)}&{_pct(ats)}".encode()
    signature = hmac.new(signing_key, base_string.encode(), hashlib.sha1).digest()
    oauth_signature = base64.b64encode(signature).decode()

    auth_params = {**oauth_params, "oauth_signature": oauth_signature}
    return "OAuth " + ", ".join(f'{_pct(k)}="{_pct(v)}"' for k, v in auth_params.items())

# ------------------------------------------------------------------------------
# Public: post_to_x
# ------------------------------------------------------------------------------

def _trim_to_tweet(text: str, limit: int = 280) -> str:
    # Twitter/X counts code points; this naive trim is acceptable here.
    t = text.strip()
    return t if len(t) <= limit else (t[: limit - 1].rstrip() + "…")

def post_to_x(text: str) -> bool:
    """
    Post `text` to X via v1.1 statuses/update.json using OAuth 1.0a.
    Honors X_ENABLED=1, records success/error to x_state.json for /status.
    Returns True on HTTP 2xx, False otherwise.
    """
    _load_env_once()

    if os.getenv("X_ENABLED", "0") != "1":
        record_x_attempt(False, "not configured: disabled", text)
        return False

    ok, ck, cs, at, ats = _gather_creds()
    if not ok:
        record_x_attempt(False, "missing secrets", text)
        return False

    url = "https://api.twitter.com/1.1/statuses/update.json"
    body = {"status": _trim_to_tweet(text)}
    auth_header = _oauth1_header("POST", url, body, ck, cs, at, ats)

    try:
        import requests  # local import to avoid hard dep at import-time
        resp = requests.post(
            url,
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode(body),
            timeout=20,
        )
        if 200 <= resp.status_code < 300:
            record_x_attempt(True, None, text)
            return True

        # Parse error body if possible
        err = ""
        try:
            j = resp.json()
            if isinstance(j, dict) and "errors" in j:
                # Typical v1.1 error
                err = "; ".join(f"{e.get('code')}: {e.get('message')}" for e in j.get("errors", []))
            elif isinstance(j, dict) and "detail" in j:
                err = str(j.get("detail"))
            else:
                err = json.dumps(j)[:300]
        except Exception:
            err = (resp.text or "")[:300]

        record_x_attempt(False, f"HTTP {resp.status_code}: {err}", text)
        return False

    except Exception as e:
        record_x_attempt(False, f"{type(e).__name__}: {e}", text)
        return False
