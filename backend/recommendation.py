import pandas as pd
from backend.model_ml import train_model, predict_price
from backend.signal_engine import generate_signal


# ==============================
# ⚡ FAST SCORE STOCK (LIGHT)
# ==============================
def score_stock(df):
    try:
        if df is None or len(df) < 50:
            return None

        df = df.sort_values("Date")

        # 👉 USE ONLY LAST 100 ROWS (BIG SPEED BOOST)
        df = df.tail(100)

        model_tuple = train_model(df)
        if model_tuple is None:
            return None

        predicted_price, _ = predict_price(model_tuple, df)

        last_row = df.iloc[-1]
        current_price = float(last_row["Close"])

        signal, confidence = generate_signal(last_row, predicted_price)

        change_pct = ((predicted_price - current_price) / current_price) * 100

        score = abs(change_pct) * 2 + confidence

        return {
            "Symbol": last_row["Symbol"],
            "Score": round(score, 2),
            "Signal": signal,
            "Confidence": confidence,
            "Current Price": round(current_price, 2),
            "Predicted Price": round(predicted_price, 2),
            "Change (%)": round(change_pct, 2)
        }

    except Exception as e:
        print(f"[ERROR STOCK]: {e}")
        return None


# ==============================
# 🚀 FAST RECOMMENDATIONS
# ==============================
def get_recommendations(full_df):

    results = []

    symbols = full_df["Symbol"].dropna().unique()

    # 🔥 LIMIT STOCKS (CRITICAL FIX)
    symbols = symbols[:10]   # only top 10 → fast

    for symbol in symbols:
        try:
            stock_df = full_df[full_df["Symbol"] == symbol]

            result = score_stock(stock_df)

            if result:
                results.append(result)

        except Exception as e:
            print(f"[ERROR {symbol}]: {e}")

    if not results:
        return pd.DataFrame(), pd.DataFrame()

    df_results = pd.DataFrame(results)

    top_buy = df_results.sort_values(by="Score", ascending=False).head(5)
    top_sell = df_results.sort_values(by="Score", ascending=True).head(5)

    return top_buy, top_sell