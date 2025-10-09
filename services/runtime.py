import os, logging, requests
from requests_oauthlib import OAuth1
from config import HAS_X, X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET

X_API_BASE = os.getenv("X_API_BASE", "https://api.twitter.com").rstrip("/")

def _oauth1():
    if not HAS_X:
        raise RuntimeError("X not configured")
    return OAuth1(
        X_CONSUMER_KEY, X_CONSUMER_SECRET,
        X_ACCESS_TOKEN,  X_ACCESS_SECRET,
        signature_type='auth_header',
    )

def post_to_x(text: str) -> tuple[bool, str]:
    """Post a simple text tweet via X v2. Returns (ok, message_or_error)."""
    try:
        url = f"{X_API_BASE}/2/tweets"
        resp = requests.post(url, json={"text": text}, auth=_oauth1(), timeout=15)
        if resp.status_code in (200, 201):
            data = resp.json()
            tid = (data.get("data") or {}).get("id")
            return True, f"posted: {tid}"
        return False, f"{resp.status_code}: {resp.text}"
    except Exception as e:
        logging.exception("post_to_x failed")
        return False, str(e)
