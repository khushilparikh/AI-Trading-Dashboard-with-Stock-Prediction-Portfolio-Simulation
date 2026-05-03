import pandas as pd

# ==============================
# PORTFOLIO BUILDER
# ==============================
def build_portfolio(recommendations, risk_level="medium"):

    if recommendations is None or recommendations.empty:
        return pd.DataFrame()

    df = recommendations.copy()

    # Clean data
    df = df.dropna()

    # -----------------------------
    # SAFE COLUMN CHECK
    # -----------------------------
    def safe_sort(df, column, fallback="confidence"):
        if column in df.columns:
            return df.sort_values(by=column, ascending=False)
        elif fallback in df.columns:
            return df.sort_values(by=fallback, ascending=False)
        else:
            return df

    # -----------------------------
    # RISK LEVEL LOGIC
    # -----------------------------
    risk_level = str(risk_level).lower()

    if risk_level == "low":
        df_sorted = safe_sort(df, "confidence")

        portfolio = df_sorted.head(3)

    elif risk_level == "medium":
        df_sorted = safe_sort(df, "score")

        portfolio = df_sorted.head(5)

    elif risk_level == "high":
        df_sorted = safe_sort(df, "change_pct")

        portfolio = df_sorted.head(7)

    else:
        # fallback to medium
        df_sorted = safe_sort(df, "score")
        portfolio = df_sorted.head(5)

    # -----------------------------
    # OPTIONAL: DIVERSIFICATION
    # -----------------------------
    if "Sector" in portfolio.columns:
        portfolio = portfolio.drop_duplicates(subset="Sector")

    # -----------------------------
    # FINAL CLEAN
    # -----------------------------
    portfolio = portfolio.reset_index(drop=True)

    return portfolio