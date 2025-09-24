import os, time, requests
DEX_URL_TOKEN = "https://api.dexscreener.com/latest/dex/tokens/{id}"
DEX_URL_SEARCH = "https://api.dexscreener.com/latest/dex/search?q={q}"
TIMEOUT = 10
_cache = {"key": None, "data": None, "ts": 0, "ttl": 60}
def _http_json(url: str):
    r = requests.get(url, timeout=TIMEOUT, headers={"Accept":"application/json"})
    r.raise_for_status(); return r.json()
def _pick_pair(payload):
    pairs = (payload or {}).get("pairs") or []
    if not pairs: return None
    return sorted(pairs, key=lambda p: float(p.get("volume", {}).get("h24") or 0), reverse=True)[0]
def _format_anchor(pair):
    price = pair.get("priceUsd") or pair.get("priceNative") or "?"
    change = pair.get("priceChange", {}).get("h24"); vol24 = pair.get("volume", {}).get("h24")
    try: price = f"${float(price):,.6f}".rstrip("0").rstrip(".")
    except: pass
    try: change_txt = f"{float(change):+.2f}%"
    except: change_txt = "±0.00%"
    try: vol24_txt = f"${float(vol24):,.0f}"
    except: vol24_txt = "$0"
    symbol = pair.get("baseToken", {}).get("symbol") or "TOKEN"
    return {"symbol":symbol,"price":price,"change24":change_txt,"vol24":vol24_txt,
            "chain":pair.get("chainId") or pair.get("chain") or "",
            "dex":pair.get("dexId") or "","pair":pair.get("pairAddress") or ""}
def get_anchor(token_id: str):
    now = time.time()
    if _cache["key"] == token_id and now - _cache["ts"] < _cache["ttl"]:
        return _cache["data"]
    try:
        j = _http_json(DEX_URL_TOKEN.format(id=token_id)); pair = _pick_pair(j)
        if not pair:
            j = _http_json(DEX_URL_SEARCH.format(q=token_id)); pair = _pick_pair(j)
        if not pair: return None
        data = _format_anchor(pair); _cache.update({"key":token_id,"data":data,"ts":now}); return data
    except Exception: return None
