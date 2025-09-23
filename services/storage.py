import os, json
from typing import Any, Dict
from config import SETTINGS
STATE_FILE = os.path.join(SETTINGS.DATA_DIR, "state.json")
LOG_FILE = os.path.join(SETTINGS.DATA_DIR, "price_log.jsonl")
os.makedirs(SETTINGS.DATA_DIR, exist_ok=True)
class KV:
    @staticmethod
    def get() -> Dict[str, Any]:
        if not os.path.exists(STATE_FILE): return {}
        with open(STATE_FILE, "r") as f: return json.load(f)
    @staticmethod
    def set(state: Dict[str, Any]):
        with open(STATE_FILE, "w") as f: json.dump(state, f, indent=2)
    @staticmethod
    def log(line: Dict[str, Any]):
        with open(LOG_FILE, "a") as f: f.write(json.dumps(line) + "\n")
