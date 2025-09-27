import os
from dataclasses import dataclass
from typing import List

TELEGRAM_SCOPE   = os.getenv("TELEGRAM_SCOPE", "all")
RITUAL_TOKEN     = os.getenv("RITUAL_TOKEN", "WEEDCOIN").upper()
X_RELAY_DEFAULT  = os.getenv("X_RELAY_DEFAULT", "off").lower() == "on"

PRICE_TTL_SEC = int(os.getenv("PRICE_TTL_SEC", "60"))
NEWS_TTL_SEC  = int(os.getenv("NEWS_TTL_SEC",  "600"))

@dataclass(frozen=True)
class Hub:
    name: str
    tzid: str

HUBS: List[Hub] = [
    Hub("Tokyo",        "Asia/Tokyo"),
    Hub("Seoul",        "Asia/Seoul"),
    Hub("Singapore",    "Asia/Singapore"),
    Hub("Sydney",       "Australia/Sydney"),
    Hub("Dubai",        "Asia/Dubai"),
    Hub("Delhi",        "Asia/Kolkata"),
    Hub("Johannesburg", "Africa/Johannesburg"),
    Hub("Zurich",       "Europe/Zurich"),
    Hub("Paris",        "Europe/Paris"),
    Hub("London",       "Europe/London"),
    Hub("Reykjavík",    "Atlantic/Reykjavik"),
    Hub("São Paulo",    "America/Sao_Paulo"),
    Hub("New York",     "America/New_York"),
    Hub("Chicago",      "America/Chicago"),
    Hub("Los Angeles",  "America/Los_Angeles"),
]

REGIONS = {
    "NorCal":     "America/Los_Angeles",
    "SoCal":      "America/Los_Angeles",
    "Denver":     "America/Denver",
    "Vancouver":  "America/Vancouver",
    "Toronto":    "America/Toronto",
    "Jamaica":    "America/Jamaica",
    "Amsterdam":  "Europe/Amsterdam",
    "Barcelona":  "Europe/Madrid",
    "Berlin":     "Europe/Berlin",
    "Uruguay":    "America/Montevideo",
}

NEWS_SOURCES = ["CoinDesk", "CoinTelegraph", "Decrypt", "The Block", "DL News"]
