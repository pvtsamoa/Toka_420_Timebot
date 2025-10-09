import json
from pathlib import Path
PATH_STATE = Path("data/chat_state.json")
def _load():
    if not PATH_STATE.exists(): return {}
    try: return json.loads(PATH_STATE.read_text())
    except Exception: return {}
def _save(obj):
    PATH_STATE.parent.mkdir(parents=True, exist_ok=True)
    PATH_STATE.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
def get_chat_token(chat_id, default_token=""):
    d=_load(); return (d.get(str(chat_id)) or {}).get("token", default_token)
def set_chat_token(chat_id, token:str):
    d=_load(); k=str(chat_id); rec=d.get(k) or {}
    rec["token"]=(token or "").strip(); d[k]=rec; _save(d); return rec["token"]
