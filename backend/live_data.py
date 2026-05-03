import requests
import pandas as pd

# ==============================
# GET LIVE PRICE (SAFE VERSION)
# ==============================
def get_live_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if "chart" not in data or data["chart"]["result"] is None:
            return None

        result = data["chart"]["result"][0]

        price = result.get("meta", {}).get("regularMarketPrice", None)

        if price is None:
            return None

        return float(price)

    except Exception as e:
        print(f"[LIVE DATA ERROR] {symbol}: {e}")
        return None


# ==============================
# ADD LIVE PRICES (OPTIMIZED)
# ==============================
def add_live_prices(df):
    df = df.copy()

    symbols = df["Symbol"].dropna().unique()

    live_prices = {}

    for sym in symbols:
        price = get_live_price(sym)

        if price is not None:
            live_prices[sym] = price

    df["Live_Price"] = df["Symbol"].map(live_prices)

    return df