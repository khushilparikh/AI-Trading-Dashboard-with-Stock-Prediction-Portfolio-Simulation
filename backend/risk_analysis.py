import pandas as pd
import numpy as np

# ==============================
# CALCULATE RETURNS
# ==============================
def calculate_returns(portfolio_df):
    if portfolio_df is None or portfolio_df.empty:
        return None

    if "Total" not in portfolio_df.columns:
        return None

    df = portfolio_df.copy()

    df = df.sort_values("Date")

    df["Returns"] = df["Total"].pct_change()

    # Clean data
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["Returns"])

    if df.empty:
        return None

    return df


# ==============================
# MAX DRAWDOWN (NEW)
# ==============================
def calculate_max_drawdown(df):
    cumulative = (1 + df["Returns"]).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak

    return drawdown.min()


# ==============================
# RISK METRICS
# ==============================
def calculate_risk_metrics(portfolio_df, risk_free_rate=0.05):

    df = calculate_returns(portfolio_df)

    if df is None:
        return None

    returns = df["Returns"]

    mean_return = returns.mean()
    std_dev = returns.std()

    if std_dev == 0 or np.isnan(std_dev):
        return None

    # Annualization (252 trading days)
    annual_return = mean_return * 252
    annual_volatility = std_dev * np.sqrt(252)

    # Sharpe Ratio
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility

    # Max Drawdown
    max_drawdown = calculate_max_drawdown(df)

    return {
        "Annual Return (%)": round(annual_return * 100, 2),
        "Volatility (%)": round(annual_volatility * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown * 100, 2)
    }