import pandas as pd

# ==============================
# SECTOR MAPPING (EXPANDABLE)
# ==============================
SECTOR_MAP = {
    "RELIANCE": "Energy",
    "TCS": "IT",
    "INFY": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "LT": "Infrastructure",
    "BHARTIARTL": "Telecom",
    "BAJFINANCE": "Finance",
    "BAJAJ-AUTO": "Auto",
    "MARUTI": "Auto"
}


# ==============================
# SECTOR ANALYSIS FUNCTION
# ==============================
def analyze_sectors(df):
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    results = []

    symbols = df["Symbol"].dropna().unique()

    for sym in symbols:
        try:
            stock = df[df["Symbol"] == sym].copy()

            if stock.empty or "Close" not in stock.columns:
                continue

            # 🔥 SORT DATA (VERY IMPORTANT)
            stock = stock.sort_values("Date").dropna(subset=["Close"])

            if len(stock) < 5:
                continue

            last_close = float(stock["Close"].iloc[-1])
            prev_close = float(stock["Close"].iloc[-5])

            # Safety check
            if prev_close <= 0:
                continue

            change = ((last_close - prev_close) / prev_close) * 100

            sector = SECTOR_MAP.get(sym, "Other")

            results.append({
                "Symbol": sym,
                "Sector": sector,
                "Change (%)": round(change, 2)
            })

        except Exception as e:
            print(f"[SECTOR ERROR] {sym}: {e}")
            continue

    if not results:
        return pd.DataFrame()

    sector_df = pd.DataFrame(results)

    # ==============================
    # SECTOR SUMMARY
    # ==============================
    sector_summary = (
        sector_df.groupby("Sector")["Change (%)"]
        .mean()
        .reset_index()
        .sort_values(by="Change (%)", ascending=False)
    )

    return sector_summary