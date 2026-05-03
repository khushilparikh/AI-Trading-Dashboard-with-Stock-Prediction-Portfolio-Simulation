import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import tensorflow as tf

# ==============================
# SET SEED (REPRODUCIBILITY)
# ==============================
np.random.seed(42)
tf.random.set_seed(42)

# ==============================
# PREPARE DATA FOR LSTM
# ==============================
def prepare_data(df, sequence_length=60):

    required_cols = ["Close", "RSI", "MACD"]

    if not all(col in df.columns for col in required_cols):
        return None, None, None

    df = df[required_cols].copy()

    # 🚨 HANDLE NaNs
    df = df.ffill().bfill().dropna()

    if len(df) <= sequence_length:
        return None, None, None

    data = df.values

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    X, y = [], []

    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i])
        y.append(data_scaled[i, 0])  # Predict Close

    return np.array(X), np.array(y), scaler


# ==============================
# BUILD MODEL
# ==============================
def build_model(input_shape):
    model = Sequential()

    model.add(LSTM(64, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(32))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    return model


# ==============================
# TRAIN MODEL
# ==============================
def train_model(X, y, epochs=5):

    if X is None or y is None:
        return None

    model = build_model((X.shape[1], X.shape[2]))

    model.fit(
        X, y,
        epochs=epochs,
        batch_size=32,
        verbose=0
    )

    return model


# ==============================
# PREDICT NEXT PRICE
# ==============================
def predict_next(model, df, scaler, sequence_length=60):

    if model is None or scaler is None:
        return None

    required_cols = ["Close", "RSI", "MACD"]

    df = df[required_cols].copy()
    df = df.ffill().bfill().dropna()

    if len(df) <= sequence_length:
        return None

    last_sequence = df.values[-sequence_length:]

    last_scaled = scaler.transform(last_sequence)

    X_input = np.array([last_scaled])

    prediction_scaled = model.predict(X_input, verbose=0)[0][0]

    # 🔥 FIXED INVERSE SCALING
    dummy = np.zeros((1, last_sequence.shape[1]))
    dummy[0, 0] = prediction_scaled

    predicted_price = scaler.inverse_transform(dummy)[0][0]

    return float(predicted_price)


# ==============================
# TESTING
# ==============================
if __name__ == "__main__":
    from data_loader import load_all_data
    from indicators import apply_indicators

    df = load_all_data()
    df = apply_indicators(df)

    stock = df[df["Symbol"] == df["Symbol"].unique()[0]]

    X, y, scaler = prepare_data(stock)

    model = train_model(X, y)

    predicted = predict_next(model, stock, scaler)

    print("Predicted Next Close Price:", predicted)