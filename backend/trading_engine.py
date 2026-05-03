import pandas as pd

# ==============================
# INITIAL WALLET
# ==============================
INITIAL_BALANCE = 100000


# ==============================
# INIT PORTFOLIO
# ==============================
def init_portfolio():
    return {
        "balance": INITIAL_BALANCE,
        "positions": {}  # {symbol: {"qty": int, "avg_price": float}}
    }


# ==============================
# BUY STOCK
# ==============================
def buy_stock(portfolio, symbol, price, qty):
    if qty <= 0:
        return portfolio, "Invalid quantity"

    total_cost = price * qty

    if portfolio["balance"] < total_cost:
        return portfolio, "Insufficient balance"

    # Deduct balance
    portfolio["balance"] -= total_cost

    # Update position
    if symbol in portfolio["positions"]:
        pos = portfolio["positions"][symbol]

        total_qty = pos["qty"] + qty
        avg_price = ((pos["avg_price"] * pos["qty"]) + total_cost) / total_qty

        portfolio["positions"][symbol] = {
            "qty": total_qty,
            "avg_price": avg_price
        }

    else:
        portfolio["positions"][symbol] = {
            "qty": qty,
            "avg_price": price
        }

    return portfolio, f"Bought {qty} shares of {symbol}"


# ==============================
# SELL STOCK
# ==============================
def sell_stock(portfolio, symbol, price, qty):
    if symbol not in portfolio["positions"]:
        return portfolio, "No position found"

    pos = portfolio["positions"][symbol]

    if qty > pos["qty"]:
        return portfolio, "Not enough shares"

    # Add balance
    portfolio["balance"] += price * qty

    # Update quantity
    remaining_qty = pos["qty"] - qty

    if remaining_qty == 0:
        del portfolio["positions"][symbol]
    else:
        portfolio["positions"][symbol]["qty"] = remaining_qty

    return portfolio, f"Sold {qty} shares of {symbol}"


# ==============================
# CALCULATE PNL
# ==============================
def calculate_portfolio_value(portfolio, df):
    total_value = portfolio["balance"]

    positions_data = []

    for symbol, pos in portfolio["positions"].items():
        stock = df[df["Symbol"] == symbol]

        if stock.empty:
            continue

        current_price = float(stock.iloc[-1]["Close"])

        position_value = current_price * pos["qty"]
        pnl = (current_price - pos["avg_price"]) * pos["qty"]

        total_value += position_value

        positions_data.append({
            "Symbol": symbol,
            "Quantity": pos["qty"],
            "Avg Price": round(pos["avg_price"], 2),
            "Current Price": round(current_price, 2),
            "P&L": round(pnl, 2)
        })

    return total_value, pd.DataFrame(positions_data)