from services.schedule_state import get_relay_on_default, set_relay_on
def is_on() -> bool:
    return get_relay_on_default()
def toggle(to: bool | None = None) -> bool:
    if to is None:
        return set_relay_on(not is_on())
    return set_relay_on(bool(to))
