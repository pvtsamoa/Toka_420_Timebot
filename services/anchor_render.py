def _fmt_usd(n:float)->str:
    if n>=1e9:return f"${n/1e9:.2f}B"
    if n>=1e6:return f"${n/1e6:.2f}M"
    if n>=1e3:return f"${n/1e3:.2f}k"
    return f"${n:.2f}"
def _fmt_price(p:float)->str:
    if p==0:return "$0.00"
    if p<0.01:return f"${p:.6f}"
    if p<1:return f"${p:.4f}"
    return f"${p:.2f}"
def _fmt_change(c:float)->str:
    return ("▲" if c>=0 else "▼")+f" {c:.2f}%"
def render_kiss_anchor(symbol:str,price:float,change_pct:float,vol_usd:float)->str:
    return f"{symbol.upper()} {_fmt_price(price)} | 24h Δ {_fmt_change(change_pct)} | 24h Vol {_fmt_usd(vol_usd)}"
