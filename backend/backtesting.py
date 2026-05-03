import pandas as pd
from backend.model_ml import train_model, predict_price
from backend.signal_engine import generate_signal


# ==============================
# BACKTEST STRATEGY
# ==============================
def run_backtest(df):
    if df is None or df.empty:
        return None

    df = df.copy()

    # Ensure sorted data
    df = df.sort_values("Date").reset_index(drop=True)

    if len(df) < 100:
        return None

    balance = 100000  # starting capital
    position = 0      # shares
    trades = []
    equity_curve = []

    transaction_cost = 0.001  # 0.1%

    for i in range(50, len(df) - 1):
        data = df.iloc[:i].copy()

        # Train model
        model_tuple = train_model(data)

        if model_tuple is None:
            continue

        predicted_price, _ = predict_price(model_tuple, data, None)

        last_row = data.iloc[-1]

        # Safety check
        if pd.isna(last_row["Close"]) or last_row["Close"] <= 0:
            continue

        price = float(last_row["Close"])

        signal, confidence = generate_signal(last_row, predicted_price)

        # ==========================
        # BUY
        # ==========================
        if signal == "BUY" and balance > price:
            qty = int(balance // price)

            cost = qty * price
            cost += cost * transaction_cost  # add fees

            balance -= cost
            position += qty

            trades.append(("BUY", price, qty))

        # ==========================
        # SELL
        # ==========================
        elif signal == "SELL" and position > 0:
            revenue = position * price
            revenue -= revenue * transaction_cost  # deduct fees

            balance += revenue

            trades.append(("SELL", price, position))
            position = 0

        # Track equity
        total_value = balance + position * price
        equity_curve.append(total_value)

    # ==============================
    # FINAL VALUE
    # ==============================
    final_price = df["Close"].iloc[-1]

    if pd.isna(final_price) or final_price <= 0:
        final_price = 0

    total_value = balance + position * final_price

    return {
        "Initial Capital": 100000,
        "Final Value": round(total_value, 2),
        "Profit": round(total_value - 100000, 2),
        "Trades": len(trades),
        "Equity Curve": equity_curve  # 🔥 important for charts
    }