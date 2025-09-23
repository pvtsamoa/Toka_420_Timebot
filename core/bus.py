from collections import defaultdict
from typing import Callable, Dict, List, Any
import logging
log = logging.getLogger("bus")
class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
    def on(self, event: str, fn: Callable[[Any], None]): self._subs[event].append(fn)
    def safe_emit(self, event: str, payload: Any):
        for fn in list(self._subs.get(event, [])):
            try: fn(payload)
            except Exception as e: log.warning("handler error for %s: %s", event, e)
BUS = EventBus()
