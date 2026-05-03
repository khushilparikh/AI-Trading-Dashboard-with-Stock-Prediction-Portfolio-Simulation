import pandas as pd
import os

# ==============================
# DYNAMIC DATA PATH (FIXED)
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "..", "data")


# ==============================
# LOAD ALL DATA
# ==============================
def load_all_data():
    all_data = []

    if not os.path.exists(DATA_FOLDER):
        raise FileNotFoundError(f"Data folder '{DATA_FOLDER}' not found")

    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

    if not files:
        raise ValueError("No CSV files found in data folder")

    for file in files:
        file_path = os.path.join(DATA_FOLDER, file)

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"[ERROR] Reading {file}: {e}")
            continue

        if df.empty:
            print(f"[SKIP] Empty file: {file}")
            continue

        # -----------------------------
        # CLEAN COLUMN NAMES
        # -----------------------------
        df.columns = [col.strip().replace(" ", "_") for col in df.columns]

        # -----------------------------
        # RENAME COLUMNS
        # -----------------------------
        df.rename(columns={
            "%Deliverble": "Deliverable_Percentage",
            "%Deliverable": "Deliverable_Percentage"
        }, inplace=True)

        # -----------------------------
        # REQUIRED COLUMNS CHECK
        # -----------------------------
        required_cols = ["Date", "Close"]
        if not all(col in df.columns for col in required_cols):
            print(f"[SKIP] Missing required columns in {file}")
            continue

        # -----------------------------
        # DATE CONVERSION
        # -----------------------------
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        # -----------------------------
        # NUMERIC CONVERSION
        # -----------------------------
        numeric_cols = [
            "Open", "High", "Low", "Close", "Last",
            "VWAP", "Volume", "Turnover",
            "Trades", "Deliverable_Volume"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # -----------------------------
        # SYMBOL HANDLING
        # -----------------------------
        if "Symbol" not in df.columns:
            df["Symbol"] = file.replace(".csv", "")
        else:
            df["Symbol"] = df["Symbol"].astype(str).str.strip()

        # -----------------------------
        # HANDLE MISSING VALUES (SAFE)
        # -----------------------------
        df = df.ffill().bfill()

        # Drop rows only if critical values missing
        df = df.dropna(subset=["Close"])

        # -----------------------------
        # REMOVE DUPLICATES
        # -----------------------------
        df = df.drop_duplicates(subset=["Symbol", "Date"])

        all_data.append(df)

    # -----------------------------
    # FINAL CHECK
    # -----------------------------
    if not all_data:
        raise ValueError("No valid data loaded. Check CSV files.")

    combined_df = pd.concat(all_data, ignore_index=True)

    # -----------------------------
    # SORT DATA
    # -----------------------------
    combined_df = combined_df.sort_values(
        by=["Symbol", "Date"]
    ).reset_index(drop=True)

    return combined_df


# ==============================
# TESTING
# ==============================
if __name__ == "__main__":
    df = load_all_data()
    print(df.head())
    print("Total rows:", len(df))
    print("Unique stocks:", df["Symbol"].nunique())