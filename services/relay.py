import os, tweepy
from .log import get_logger
logger = get_logger()

class XRelay:
    def __init__(self, enabled_default: bool):
        self.enabled = enabled_default
        self._client = None
        if self.enabled:
            self._boot()

    def _boot(self):
        k = os.getenv
        ak, as_, at, ats = k("X_API_KEY"), k("X_API_SECRET"), k("X_ACCESS_TOKEN"), k("X_ACCESS_SECRET")
        if not all([ak, as_, at, ats]):
            logger.info("X relay disabled: missing credentials.")
            self.enabled = False
            return
        try:
            auth = tweepy.OAuth1UserHandler(ak, as_, at, ats)
            self._client = tweepy.API(auth)
            self._client.verify_credentials()
            logger.info("X relay ready.")
        except Exception as e:
            logger.exception("X relay init failed: %s", e)
            self.enabled = False

    def toggle(self, on: bool):
        prev = self.enabled
        self.enabled = on
        if on and self._client is None:
            self._boot()
        return prev, self.enabled

    def post(self, text: str) -> bool:
        if not self.enabled or self._client is None:
            return False
        try:
            self._client.update_status(status=text[:280])
            logger.info("Posted to X.")
            return True
        except Exception as e:
            logger.exception("X post failed: %s", e)
            return False
