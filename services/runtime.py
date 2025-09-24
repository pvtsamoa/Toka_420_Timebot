import os, re, logging
try:
    import tweepy
except Exception:
    tweepy = None

TAG_HANDLE = "@weedcoinog"
TAG_RE     = re.compile(r"(?i)@weedcoinog\b")
HASH_RE    = re.compile(r"(?i)#weedcoin\b")
TICK_RE    = re.compile(r"(?i)\$weedcoin\b")

def enforce_tags(s: str) -> str:
    extras = []
    if not TAG_RE.search(s):  extras.append(TAG_HANDLE)
    if not HASH_RE.search(s): extras.append("#Weedcoin")
    if not TICK_RE.search(s): extras.append("$weedcoin")
    return (s + " " + " ".join(extras)).strip()

def build_x_text(hub_name: str, token: str) -> str:
    # Keep message short; token is currently fixed to $weedcoin in branding
    return f"{hub_name} 4:20 • $weedcoin"

def post_to_x(text: str):
    text = enforce_tags(text)
    if tweepy is None:
        logging.warning("[X relay] Tweepy not installed; skipping")
        return
    k = os.getenv("X_API_KEY"); s = os.getenv("X_API_SECRET")
    at = os.getenv("X_ACCESS_TOKEN"); as_ = os.getenv("X_ACCESS_SECRET")
    if not all([k, s, at, as_]):
        logging.warning("[X relay] Missing API creds; skipping")
        return
    try:
        auth = tweepy.OAuth1UserHandler(k, s, at, as_)
        api = tweepy.API(auth)
        api.update_status(status=text)
        logging.info("[X] posted: %s", text)
    except Exception as e:
        logging.warning("[X relay error] %s", e)
