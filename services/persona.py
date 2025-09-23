from typing import Tuple
def toka_anchor_line(symbol: str, anchor: Tuple[float,float,float]) -> str:
    price, pct, vol = anchor; sign = "↑" if pct >= 0 else "↓"
    return (
        f"🌿 Toka 4:20 anchor — {symbol}\n"
        f"24h {pct:.2f}% {sign} |  | vol \n"
        f"Keep your canoe balanced. Bongterm > FOMO."
    )
