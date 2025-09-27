from typing import Dict, List
from config import REGIONS, NEWS_SOURCES

def sources_by_region() -> Dict[str, List[str]]:
    return {region: list(NEWS_SOURCES) for region in REGIONS.keys()}
