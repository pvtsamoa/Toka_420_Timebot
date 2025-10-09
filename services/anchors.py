import time, os, requests
TTL_SECONDS=int(os.environ.get("TOKA_ANCHOR_TTL","90"))
DEX_URL="https://api.dexscreener.com/latest/dex/search?q={q}"
_cache={}
def _now(): return int(time.time())
def _cache_get(k):
    i=_cache.get(k)
    if not i: return None
    ts,d=i; return d if _now()-ts<TTL_SECONDS else None
def _cache_set(k,d): _cache[k]=(_now(),d)
def _pick_top_pair(p):
    pairs=(p or {}).get("pairs") or []
    if not pairs: return None
    pairs.sort(key=lambda x:(float((x.get('liquidity') or {}).get('usd') or 0),
                              float((x.get('volume') or {}).get('h24') or 0)), reverse=True)
    return pairs[0]
def get_anchor(q:str)->dict:
    q=(q or "").strip()
    if not q: raise ValueError("empty query")
    key=f"anchor:{q.lower()}"; c=_cache_get(key)
    if c: return c
    r=requests.get(DEX_URL.format(q=q),timeout=10); r.raise_for_status()
    data=r.json(); top=_pick_top_pair(data)
    if not top: raise RuntimeError(f"No pair found for {q}")
    sym=((top.get("baseToken") or {}).get("symbol") or q).upper()
    price=float(top.get("priceUsd") or 0.0)
    change=float((top.get("priceChange") or {}).get("h24") or 0.0)
    vol24=float((top.get("volume") or {}).get("h24") or 0.0)
    out={"symbol":sym,"price":price,"change24h_pct":change,"volume24h_usd":vol24}
    _cache_set(key,out); return out
