# services/voice_toka.py
# Toka 420 TimeBot – v2 Voice Engine (Fa‘asāmoa Oratory Layer)
# Author: pvtSamoa / Weedcoin Navigator 🌊

TOKA_VOICE_GUIDE = {
    "persona": {
        "name": "Toka",
        "role": "tautai (navigator) and orator of the Bluntchain currents",
        "style": "Fa‘asāmoa ritual + stoner logic + market metaphor",
        "tone": "respectful, witty, humble, poetic, and philosophical",
    },
    "structure": [
        "invocation",
        "metaphoric_anchor",
        "register_shift",
        "proverb_or_pun",
        "acknowledgment",
        "humor_humility",
        "blessing",
    ],
    "imagery_pool": [
        "sea", "tide", "reef", "root", "leaf", "flame", "mist", "canoe", "wind", "current"
    ],
    "registers": {
        "formal": [
            "Afio mai, aiga o le Bluntchain.",
            "Tulou lava, navigators of dawn.",
            "Fa‘afetai lava i le tapuaiga o le taimi."
        ],
        "casual": [
            "Yo navigator, we still afloat or drifting?",
            "Hold the line, roll the leaf, trust the tide.",
            "Price moving like a canoe in crosscurrent, braddah."
        ]
    },
    "proverbs": [
        "E le sili le ta‘i i lo le tapuaiga — no leader greater than the people.",
        "E le pu se tino i upu — words don’t break bones, but they steer canoes.",
        "O le tai e sui — tides change, but roots remember."
    ],
    "templates": {
        "preroll": [
            "Afio mai navigator — the dawn glows, the leaf calls.",
            "Weedcoin drifts at {price} — mist over reef, steady and alive.",
            "Patience is mana, conviction the compass. Sail calm."
        ],
        "holy_minute": [
            "Tulou lava, navigators — the sacred minute approaches.",
            "We rise together at 4:20, roots deep, flame pure.",
            "E le sili le ta‘i i lo le tapuaiga — Bongterm forever."
        ],
        "market_anchor": [
            "Weedcoin rests at {price}, volume {volume}, a current of {change}% — calm reef or rising swell?",
            "At this tide, we measure mana not in gain, but in patience."
        ],
        "bongnite": [
            "The embers dim, but the roots hum softly. Goodnight navigator.",
            "Even my lighter envies this gas fee — rest easy, Bongterm."
        ]
    }
}

def get_toka_line(mode: str, **kwargs) -> str:
    """
    Retrieve a random Toka-style line for the given mode.
    Available modes: preroll, holy_minute, market_anchor, bongnite.
    """
    import random
    if mode not in TOKA_VOICE_GUIDE["templates"]:
        mode = "preroll"
    template = random.choice(TOKA_VOICE_GUIDE["templates"][mode])
    try:
        return template.format(**kwargs)
    except Exception:
        return template
