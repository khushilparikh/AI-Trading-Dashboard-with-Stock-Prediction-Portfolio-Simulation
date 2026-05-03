import pandas as pd

# ==============================
# SIMULATE PORTFOLIO
# ==============================
def simulate_portfolio(df, stocks, initial_amount=100000):
    if df is None or df.empty or not stocks:
        return None

    df = df.copy()

    valid_stocks = []

    # Filter valid stocks first
    for stock in stocks:
        temp = df[df["Symbol"] == stock]

        if not temp.empty and "Close" in temp.columns:
            valid_stocks.append(stock)

    if not valid_stocks:
        return None

    allocation = initial_amount / len(valid_stocks)

    portfolio_df = pd.DataFrame()

    for stock in valid_stocks:
        temp = df[df["Symbol"] == stock].copy()

        temp = temp.sort_values("Date").drop_duplicates(subset="Date")

        # Safety check
        if temp.empty or temp["Close"].iloc[0] <= 0:
            continue

        base_price = temp["Close"].iloc[0]

        temp[stock] = (temp["Close"] / base_price) * allocation

        temp = temp[["Date", stock]]

        if portfolio_df.empty:
            portfolio_df = temp
        else:
            portfolio_df = pd.merge(
                portfolio_df,
                temp,
                on="Date",
                how="outer"
            )

    if portfolio_df.empty:
        return None

    # Sort & clean
    portfolio_df = portfolio_df.sort_values("Date")

    portfolio_df = portfolio_df.ffill().bfill()

    # Remove any remaining NaNs
    portfolio_df = portfolio_df.dropna()

    # ==============================
    # TOTAL VALUE
    # ==============================
    stock_cols = [col for col in portfolio_df.columns if col != "Date"]

    portfolio_df["Total"] = portfolio_df[stock_cols].sum(axis=1)

    return portfolio_df


# ==============================
# CALCULATE METRICS
# ==============================
def portfolio_metrics(portfolio_df, initial_amount):
    if portfolio_df is None or portfolio_df.empty:
        return None

    final_value = float(portfolio_df["Total"].iloc[-1])

    profit = final_value - initial_amount

    return_pct = (profit / initial_amount) * 100

    return {
        "Final Value": round(final_value, 2),
        "Profit": round(profit, 2),
        "Return (%)": round(return_pct, 2)
    }