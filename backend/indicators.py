import pandas as pd
import numpy as np

# ==============================
# VALIDATION
# ==============================
def validate_df(df):
    required_cols = ["Date", "Close"]

    if df is None or df.empty:
        return False

    return all(col in df.columns for col in required_cols)


# ==============================
# MOVING AVERAGES
# ==============================
def add_moving_averages(df):
    df = df.copy()

    df["SMA_20"] = df["Close"].rolling(window=20, min_periods=5).mean()
    df["SMA_50"] = df["Close"].rolling(window=50, min_periods=10).mean()

    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()

    return df


# ==============================
# RSI (EMA BASED - BETTER)
# ==============================
def add_rsi(df, period=14):
    df = df.copy()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)

    df["RSI"] = 100 - (100 / (1 + rs))

    return df


# ==============================
# MACD
# ==============================
def add_macd(df):
    df = df.copy()

    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df


# ==============================
# BOLLINGER BANDS
# ==============================
def add_bollinger_bands(df):
    df = df.copy()

    df["BB_Middle"] = df["Close"].rolling(window=20, min_periods=5).mean()
    df["BB_Std"] = df["Close"].rolling(window=20, min_periods=5).std()

    df["BB_Upper"] = df["BB_Middle"] + (2 * df["BB_Std"])
    df["BB_Lower"] = df["BB_Middle"] - (2 * df["BB_Std"])

    return df


# ==============================
# MASTER FUNCTION
# ==============================
def add_all_indicators(df):
    if not validate_df(df):
        return df

    df = df.copy()

    # Sort by date
    df = df.sort_values("Date")

    # Remove invalid rows
    df = df.dropna(subset=["Close"])

    df = add_moving_averages(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)

    # Fill only forward (avoid fake past values)
    df = df.ffill()

    return df


# ==============================
# APPLY PER STOCK
# ==============================
def apply_indicators(df):
    if df is None or df.empty:
        return df

    grouped = []

    for symbol, group in df.groupby("Symbol"):
        processed = add_all_indicators(group)
        grouped.append(processed)

    return pd.concat(grouped, ignore_index=True)


# ==============================
# TESTING
# ==============================
if __name__ == "__main__":
    from data_loader import load_all_data

    df = load_all_data()
    df = apply_indicators(df)

    print(df.tail())
    print("Columns:", df.columns)