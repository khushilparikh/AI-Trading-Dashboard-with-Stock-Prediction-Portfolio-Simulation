import numpy as np

# ==============================
# SIGNAL LOGIC (PRO VERSION)
# ==============================
def generate_signal(row, predicted_price):
    try:
        current_price = float(row.get("Close", 0))
        predicted_price = float(predicted_price)
    except:
        return "HOLD", 50

    if current_price <= 0:
        return "HOLD", 50

    price_diff_pct = ((predicted_price - current_price) / current_price) * 100

    # ==============================
    # AI BASE SIGNAL (PRIMARY)
    # ==============================
    if price_diff_pct >= 1.5:
        return "BUY", 85

    if price_diff_pct <= -1.5:
        return "SELL", 85

    if 0.7 <= price_diff_pct < 1.5:
        return "BUY", 70

    if -1.5 < price_diff_pct <= -0.7:
        return "SELL", 70

    # ==============================
    # INDICATOR-BASED LOGIC
    # ==============================
    signal_score = 0
    weight_total = 0

    # ------------------------------
    # RSI (weight = 1)
    # ------------------------------
    rsi = row.get("RSI", np.nan)
    if not np.isnan(rsi):
        weight_total += 1
        if rsi < 30:
            signal_score += 1
        elif rsi > 70:
            signal_score -= 1

    # ------------------------------
    # MACD (weight = 1.5)
    # ------------------------------
    macd = row.get("MACD", np.nan)
    macd_signal = row.get("MACD_Signal", np.nan)

    if not np.isnan(macd) and not np.isnan(macd_signal):
        weight_total += 1.5
        if macd > macd_signal:
            signal_score += 1.5
        elif macd < macd_signal:
            signal_score -= 1.5

    # ------------------------------
    # TREND (SMA) (weight = 2)
    # ------------------------------
    sma20 = row.get("SMA_20", np.nan)
    sma50 = row.get("SMA_50", np.nan)

    if not np.isnan(sma20) and not np.isnan(sma50):
        weight_total += 2
        if sma20 > sma50:
            signal_score += 2
        elif sma20 < sma50:
            signal_score -= 2

    # ==============================
    # NORMALIZE SCORE
    # ==============================
    if weight_total == 0:
        return "HOLD", 50

    normalized_score = signal_score / weight_total

    # ==============================
    # FINAL DECISION
    # ==============================
    if normalized_score > 0.5:
        confidence = int(55 + normalized_score * 30)
        return "BUY", min(confidence, 80)

    elif normalized_score < -0.5:
        confidence = int(55 + abs(normalized_score) * 30)
        return "SELL", min(confidence, 80)

    else:
        return "HOLD", 55


# ==============================
# APPLY SIGNAL
# ==============================
def apply_signals(df, predicted_price):

    if df is None or df.empty:
        return {
            "signal": "HOLD",
            "confidence": 50,
            "current_price": 0,
            "predicted_price": 0
        }

    last_row = df.iloc[-1]

    signal, confidence = generate_signal(last_row, predicted_price)

    return {
        "signal": signal,
        "confidence": int(confidence),
        "current_price": float(last_row.get("Close", 0)),
        "predicted_price": float(predicted_price)
    }