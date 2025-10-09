def _fmt_usd(n):
    if n is None: return "—"
    try: n = float(n)
    except Exception: return "—"
    if n >= 1e9: return f"${n/1e9:.2f}B"
    if n >= 1e6: return f"${n/1e6:.2f}M"
    if n >= 1e3: return f"${n/1e3:.2f}k"
    return f"${n:.2f}"

def _fmt_price(p):
    if p is None: return "—"
    p = float(p)
    if p == 0: return "$0.00"
    if p < 0.01: return f"${p:.6f}"
    if p < 1:   return f"${p:.4f}"
    return f"${p:.2f}"

def _fmt_change_pct(c):
    if c is None: return "—"
    c = float(c)
    return ("▲" if c >= 0 else "▼") + f" {c:.2f}%"

def _fmt_change_abs(price, pct):
    if price is None or pct is None: return "—"
    try:
        price = float(price); pct = float(pct)
    except Exception:
        return "—"
    delta = price * (pct/100.0)
    sign = "+" if delta >= 0 else "-"
    return f"{sign}${abs(delta):.6f}" if price < 0.01 else f"{sign}${abs(delta):.4f}"

def render_token_line(symbol, price, change_pct, mcap, fdv):
    cap = fdv if fdv is not None else mcap
    cap_label = "FDV" if fdv is not None else "MCap" if mcap is not None else "Cap"
    return (
        f"{(symbol or '').upper()} "
        f"{_fmt_price(price)} | "
        f"Δ {_fmt_change_abs(price, change_pct)} ({_fmt_change_pct(change_pct)}) | "
        f"{cap_label} {_fmt_usd(cap)}"
    )
