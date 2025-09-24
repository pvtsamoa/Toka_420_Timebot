import os, re
from tweepy import OAuth1UserHandler, API
TAG_HANDLE = "@weedcoinog"
TAG_RE = re.compile(r"(?i)@weedcoinog\b")
def _x_client():
    auth = OAuth1UserHandler(
        os.getenv("X_API_KEY"), os.getenv("X_API_SECRET"),
        os.getenv("X_ACCESS_TOKEN"), os.getenv("X_ACCESS_SECRET"),
    ); return API(auth)
def enforce_tag(text: str) -> str:
    if not text: return TAG_HANDLE
    return text if TAG_RE.search(text) else f"{text.rstrip()} {TAG_HANDLE}"
def post_to_x(text: str, media_paths=None):
    api = _x_client(); final = enforce_tag(text)
    if media_paths:
        ids = [api.media_upload(filename=p).media_id_string for p in media_paths]
        api.update_status(status=final, media_ids=ids)
    else:
        api.update_status(status=final)
