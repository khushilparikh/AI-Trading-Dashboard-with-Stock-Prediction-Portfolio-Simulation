# ==============================
# ALERT SYSTEM
# ==============================

# ==============================
# ALERT CHECK
# ==============================
def check_alert(signal, confidence, symbol):
    if signal == "BUY" and confidence > 70:
        return f"🟢 STRONG BUY ALERT for {symbol} ({confidence}%)"

    elif signal == "SELL" and confidence > 70:
        return f"🔴 STRONG SELL ALERT for {symbol} ({confidence}%)"

    return None


# ==============================
# MARKET SCAN
# ==============================
def scan_market(df, generate_signal, predict_price, train_model):
    alerts = []
    seen_alerts = set()  # prevent duplicates

    if df is None or df.empty:
        return alerts

    symbols = df["Symbol"].dropna().unique()

    for sym in symbols:
        try:
            stock = df[df["Symbol"] == sym].copy()

            # Safety checks
            if stock.empty or len(stock) < 50:
                continue

            # Ensure sorted data
            stock = stock.sort_values("Date")

            # Train model
            model_tuple = train_model(stock)

            if model_tuple is None:
                continue

            predicted_price, _ = predict_price(model_tuple, stock, None)

            last_row = stock.iloc[-1]

            # Generate signal
            signal, confidence = generate_signal(last_row, predicted_price)

            alert = check_alert(signal, confidence, sym)

            # Avoid duplicate alerts
            if alert and alert not in seen_alerts:
                alerts.append(alert)
                seen_alerts.add(alert)

        except Exception as e:
            # Optional: print error for debugging
            print(f"Alert error for {sym}: {e}")
            continue

    return alerts