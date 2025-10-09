from datetime import datetime, timezone

# Simple moon phase calc (conway-like; ~1% error). Returns (phase_name, illumination%)
_PHASES = [
    (0.0,  "New Moon"),
    (0.125, "Waxing Crescent"),
    (0.25, "First Quarter"),
    (0.375, "Waxing Gibbous"),
    (0.5,  "Full Moon"),
    (0.625,"Waning Gibbous"),
    (0.75, "Last Quarter"),
    (0.875,"Waning Crescent"),
    (1.0,  "New Moon")
]

def _phase_fraction(dt: datetime) -> float:
    # Days since known new moon: 2000-01-06 18:14 UTC (JDN 2451550.1)
    # Synodic month length:
    SYNODIC = 29.53058867
    # convert to UTC timestamp days
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ts_days = dt.timestamp() / 86400.0
    # epoch (2000-01-06 18:14 UTC)
    epoch = 946728840.0 / 86400.0
    days = ts_days - epoch
    return (days / SYNODIC) % 1.0

def phase_name(dt: datetime) -> str:
    f = _phase_fraction(dt)
    for thr, name in _PHASES:
        if f <= thr:
            return name
    return "New Moon"

def illumination(dt: datetime) -> int:
    f = _phase_fraction(dt)
    # 0..1 -> simulate % illumination (approx)
    # Use sine curve peaking at 0.5 (full moon)
    import math
    pct = 0.5 * (1 - math.cos(2 * math.pi * f)) * 100
    return int(round(pct))
