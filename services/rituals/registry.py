from typing import Callable, Dict
from .types import RitualKey, RitualContext
from . import templates

Registry: Dict[str, Callable[[RitualContext], str]] = {
    RitualKey.PRE_ROLL.value: templates.template_pre_roll,
    RitualKey.HOLY_MINUTE.value: templates.template_holy_minute,
}

def get_template(key: RitualKey) -> Callable[[RitualContext], str]:
    try:
        return Registry[key.value]
    except KeyError as e:
        raise KeyError(f"Unknown ritual key: {key}") from e
