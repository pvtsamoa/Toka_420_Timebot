import logging, time
from typing import Dict
log = logging.getLogger("registry")
class ModuleRegistry:
    def __init__(self):
        self.modules: Dict[str, str] = {}
        self.health: Dict[str, float] = {}
    def register(self, name: str, version: str = "4.0"):
        self.modules[name] = version; self.health[name] = time.time()
        log.info("module up: %s v%s", name, version)
    def ping(self, name: str): self.health[name] = time.time()
REGISTRY = ModuleRegistry()
