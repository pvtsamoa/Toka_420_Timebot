import sys
import json
import time
import requests

COINGECKO_COIN_URL = "https://api.coingecko.com/api/v3/coins/{}"
DEX_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search?q={}"
DEX_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"


def load_tokens(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Token list must be a JSON array")
    return data


def check_coingecko_id(cg_id: str):
    url = COINGECKO_COIN_URL.format(cg_id)
    r = requests.get(url, timeout=15, headers={"User-Agent": "Toka420Bot/1.0"})
    if r.status_code == 200:
        payload = r.json()
        return True, {"id": payload.get("id"), "symbol": payload.get("symbol"), "name": payload.get("name")}
    return False, {"status_code": r.status_code, "url": url}


def check_dex_token(mint: str):
    url = DEX_TOKEN_URL.format(mint)
    r = requests.get(url, timeout=15, headers={"User-Agent": "Toka420Bot/1.0"})
    if r.status_code != 200:
        return False, {"status_code": r.status_code, "url": url}

    payload = r.json()
    pairs = payload.get("pairs") or []
    # Consider valid if DexScreener recognizes it and returns at least one pair
    if pairs:
        # Return a compact summary
        top = pairs[0]
        return True, {
            "pairs": len(pairs),
            "chainId": top.get("chainId"),
            "dexId": top.get("dexId"),
            "pairAddress": top.get("pairAddress"),
        }
    return False, {"pairs": 0, "url": url}


def search_dex(symbol_or_name: str):
    url = DEX_SEARCH_URL.format(symbol_or_name)
    r = requests.get(url, timeout=15, headers={"User-Agent": "Toka420Bot/1.0"})
    if r.status_code != 200:
        return False, {"status_code": r.status_code, "url": url}

    payload = r.json()
    pairs = payload.get("pairs") or []
    # Return top few matches for triage
    top = []
    for p in pairs[:5]:
        top.append(
            {
                "chainId": p.get("chainId"),
                "dexId": p.get("dexId"),
                "baseSymbol": (p.get("baseToken") or {}).get("symbol"),
                "baseName": (p.get("baseToken") or {}).get("name"),
                "baseAddress": (p.get("baseToken") or {}).get("address"),
                "pairAddress": p.get("pairAddress"),
            }
        )
    return True, {"matches": len(pairs), "top": top}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "media/cannabis_tokens.json"
    tokens = load_tokens(path)

    report = []
    ok_count = 0

    for t in tokens:
        symbol = t.get("symbol")
        name = t.get("name")
        chain = (t.get("chain") or "").lower()
        cg_id = t.get("coingecko_id")
        mint = t.get("mint")

        item = {"symbol": symbol, "name": name, "chain": chain}

        # Priority 1: CoinGecko ID
        if cg_id:
            ok, info = check_coingecko_id(cg_id)
            item["coingecko_id"] = cg_id
            item["coingecko_ok"] = ok
            item["coingecko_info"] = info
            item["ok"] = ok
            report.append(item)
            ok_count += 1 if ok else 0
            time.sleep(1.2)  # be polite to CG
            continue

        # Priority 2: Solana mint via DexScreener
        if chain == "solana" and mint:
            ok, info = check_dex_token(mint)
            item["mint"] = mint
            item["dex_ok"] = ok
            item["dex_info"] = info
            item["ok"] = ok
            report.append(item)
            ok_count += 1 if ok else 0
            continue

        # Priority 3: fallback search by symbol/name (ambiguous)
        query = symbol or name or ""
        ok, info = search_dex(query)
        item["search_query"] = query
        item["search_ok"] = ok
        item["search_info"] = info
        # This is not a hard pass because symbol-only is ambiguous. Mark as needs_manual if > 1 match.
        if ok and isinstance(info.get("matches"), int):
            item["ok"] = info["matches"] > 0
            item["needs_manual"] = info["matches"] != 1
        else:
            item["ok"] = False
            item["needs_manual"] = True

        report.append(item)
        ok_count += 1 if item["ok"] else 0
        time.sleep(0.2)

    out_path = path.replace(".json", ".validation_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    total = len(tokens)
    bad = total - ok_count
    print(f"Validated: {ok_count}/{total} OK, {bad} flagged. Report: {out_path}")

    # Exit non-zero if any hard failures
    hard_fail = [r for r in report if not r.get("ok")]
    if hard_fail:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
