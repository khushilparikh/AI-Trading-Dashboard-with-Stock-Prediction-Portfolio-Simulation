import requests

# ==============================
# INDEX SYMBOLS
# ==============================
INDEX_MAP = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK"
}


# ==============================
# GET LIVE INDEX DATA
# ==============================
def get_index_data(index_symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{index_symbol}"

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        result = data["chart"]["result"][0]

        meta = result["meta"]

        return {
            "price": meta.get("regularMarketPrice"),
            "change": meta.get("regularMarketPrice") - meta.get("previousClose"),
            "change_pct": ((meta.get("regularMarketPrice") - meta.get("previousClose")) / meta.get("previousClose")) * 100
        }

    except Exception as e:
        print(f"[INDEX ERROR]: {e}")
        return None


# ==============================
# GET ALL INDICES
# ==============================
def get_all_indices():
    results = {}

    for name, symbol in INDEX_MAP.items():
        data = get_index_data(symbol)
        if data:
            results[name] = data

    return results