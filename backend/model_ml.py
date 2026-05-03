import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier

# ==============================
# FEATURE ENGINEERING
# ==============================
def add_features(df):
    df = df.sort_values("Date").copy()

    df["Return_1"] = df["Close"].pct_change()
    df["Return_3"] = df["Close"].pct_change(3)
    df["Return_5"] = df["Close"].pct_change(5)

    df["Volatility"] = df["Close"].rolling(10).std()

    return df


# ==============================
# PREPARE DATA
# ==============================
def prepare_data(df):

    required_cols = [
        "Close", "Volume", "RSI",
        "MACD", "MACD_Signal",
        "SMA_20", "SMA_50"
    ]

    if not all(col in df.columns for col in required_cols):
        return None, None, None, None

    df = add_features(df)

    df["Target_Price"] = df["Close"].shift(-1)

    df["Target_Direction"] = np.where(
        df["Target_Price"] > df["Close"], 1, 0
    )

    features = [
        "Close", "Volume", "RSI",
        "MACD", "MACD_Signal",
        "SMA_20", "SMA_50",
        "Return_1", "Return_3", "Return_5",
        "Volatility"
    ]

    df = df[features + ["Target_Price", "Target_Direction"]].dropna()

    if len(df) < 60:
        return None, None, None, None

    X = df[features]
    y_price = df["Target_Price"]
    y_dir = df["Target_Direction"]

    return X, y_price, y_dir, features


# ==============================
# TRAIN MODELS
# ==============================
def train_model(df):
    X, y_price, y_dir, features = prepare_data(df)

    if X is None:
        return None

    try:
        # Regression model (controlled)
        price_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        )
        price_model.fit(X, y_price)

        # Classification model
        dir_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        dir_model.fit(X, y_dir)

        return price_model, dir_model, features

    except Exception as e:
        print(f"[MODEL ERROR]: {e}")
        return None


# ==============================
# PREDICT
# ==============================
def predict_price(model_tuple, df, features=None):

    if model_tuple is None:
        return float(df["Close"].iloc[-1]), "HOLD"

    price_model, dir_model, features = model_tuple

    df = add_features(df)

    latest = df.dropna(subset=features)

    if latest.empty:
        return float(df["Close"].iloc[-1]), "HOLD"

    last_row = latest[features].iloc[-1:]

    try:
        current_price = float(df["Close"].iloc[-1])

        price_pred = price_model.predict(last_row)[0]

        # 🔥 CLAMP TO REALISTIC RANGE
        max_move = 0.10
        upper = current_price * (1 + max_move)
        lower = current_price * (1 - max_move)

        price_pred = max(min(price_pred, upper), lower)

        # 🔥 PROBABILITY SIGNAL
        prob = dir_model.predict_proba(last_row)[0]
        direction = dir_model.predict(last_row)[0]

        confidence = round(max(prob) * 100, 2)

        signal = "BUY" if direction == 1 else "SELL"

        return float(price_pred), signal

    except Exception as e:
        print(f"[PREDICT ERROR]: {e}")
        return float(df["Close"].iloc[-1]), "HOLD"