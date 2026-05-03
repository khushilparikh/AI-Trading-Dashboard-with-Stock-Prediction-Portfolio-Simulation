# ==============================
# FIX PATH
# ==============================
import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ==============================
# IMPORTS
# ==============================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==============================
# BACKEND IMPORTS
# ==============================
from backend.market_live import get_all_indices
from backend.data_loader import load_all_data
from backend.indicators import apply_indicators
from backend.model_ml import train_model, predict_price
from backend.signal_engine import apply_signals
from backend.recommendation import get_recommendations
from backend.news_analysis import get_stock_news, analyze_sentiment, generate_llm_summary
from backend.telegram_alerts import send_alert

# ==============================
# ⚡ PERFORMANCE OPTIMIZATION
# ==============================
@st.cache_data(show_spinner=False)
def load_data_cached():
    return load_all_data()

@st.cache_data(show_spinner=False)
def apply_indicators_cached(df):
    return apply_indicators(df)

@st.cache_resource(show_spinner=False)
def train_model_cached(df):
    return train_model(df)

@st.cache_data(show_spinner=False)
def get_recommendations_cached(df):
    return get_recommendations(df)
# ==============================
# SESSION STATE INIT
# ==============================
if "portfolio_state" not in st.session_state:
    st.session_state.portfolio_state = {
        "balance": 100000,
        "positions": {}
    }

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="AI Trading Dashboard", layout="wide")
st.title("📊 AI Trading Dashboard")

# ==============================
# LOAD DATA
# ==============================
df = load_data_cached()
df = apply_indicators_cached(df)

if df is None or df.empty:
    st.error("No data available")
    st.stop()

# ⚡ GROUP DATA (IMPORTANT)
grouped_data = dict(tuple(df.groupby("Symbol")))

# ==============================
# 📊 LIVE MARKET
# ==============================
col1, col2 = st.columns([8,1])
with col1:
    st.subheader("📊 Live Market Overview")
with col2:
    refresh_market = st.button("🔄")

if "market_data" not in st.session_state or refresh_market:
    st.session_state.market_data = get_all_indices()

indices = st.session_state.market_data

cols = st.columns(3)
for i, (name, data) in enumerate(indices.items()):
    cols[i].metric(
        name,
        round(data["price"], 2),
        f"{round(data['change'],2)} ({round(data['change_pct'],2)}%)",
        delta_color="normal" if data["change"] > 0 else "inverse"
    )

# ==============================
# STOCK SELECTION (FAST)
# ==============================
selected_stock = st.sidebar.selectbox("Select Stock", list(grouped_data.keys()))

stock_df = grouped_data.get(selected_stock)
if stock_df is None or stock_df.empty:
    st.error("Stock data not available")
    st.stop()

# ==============================
# 🤖 AI PREDICTION
# ==============================
col1, col2 = st.columns([8,1])
with col1:
    st.subheader("🤖 AI Prediction")
with col2:
    refresh_pred = st.button("🔄 Prediction")

if "predictions" not in st.session_state:
    st.session_state.predictions = {}

if selected_stock not in st.session_state.predictions or refresh_pred:
    model_tuple = train_model_cached(stock_df)
    predicted_price, _ = predict_price(model_tuple, stock_df)
    st.session_state.predictions[selected_stock] = predicted_price

predicted_price = st.session_state.predictions[selected_stock]

# ==============================
# SIGNAL
# ==============================
result = apply_signals(stock_df, predicted_price)
send_alert(result["signal"], result["confidence"], selected_stock, result["current_price"])

col1, col2, col3 = st.columns(3)
col1.metric("Current Price", result["current_price"])
col2.metric("Predicted Price", result["predicted_price"])
col3.metric("Signal", f"{result['signal']} ({result['confidence']}%)")

# ==============================
# 📈 CHART
# ==============================
fig = go.Figure(data=[go.Candlestick(
    x=stock_df["Date"],
    open=stock_df["Open"],
    high=stock_df["High"],
    low=stock_df["Low"],
    close=stock_df["Close"]
)])
st.plotly_chart(fig, use_container_width=True)

# ==============================
# 🔥 HEATMAP (FAST)
# ==============================
col1, col2 = st.columns([8,1])
with col1:
    st.subheader("🔥 Market Overview")
with col2:
    refresh_heatmap = st.button("🔄 Heatmap")

if "heatmap" not in st.session_state or refresh_heatmap:
    heatmap_data = []

    for sym, stock in grouped_data.items():
        stock = stock.sort_values("Date")

        if len(stock) < 2:
            continue

        last = stock.iloc[-1]
        prev = stock.iloc[-2]

        change = ((last["Close"] - prev["Close"]) / prev["Close"]) * 100

        heatmap_data.append({
            "Symbol": sym,
            "Price": last["Close"],
            "Change (%)": change
        })

    st.session_state.heatmap = pd.DataFrame(heatmap_data)

heatmap_df = st.session_state.heatmap

col1, col2 = st.columns(2)
col1.dataframe(heatmap_df.sort_values("Change (%)", ascending=False).head(5))
col2.dataframe(heatmap_df.sort_values("Change (%)").head(5))

# ==============================
# 📰 NEWS
# ==============================
st.subheader("🧠 News & Sentiment")

if "news_data" not in st.session_state:
    st.session_state.news_data = {}

if selected_stock not in st.session_state.news_data:
    st.session_state.news_data[selected_stock] = get_stock_news(selected_stock)

news = st.session_state.news_data[selected_stock]

for item in news:
    st.markdown(f"👉 [{item['title']}]({item['link']})")

sentiment, score, impact = analyze_sentiment(news)
summary = generate_llm_summary(selected_stock, news, sentiment, score, impact)

st.write(f"**Sentiment:** {sentiment} ({score})")
st.info(summary)

# ==============================
# 🏆 RECOMMENDATIONS (SAFE + PRO)
# ==============================
st.markdown("## 🏆 Smart Recommendations")

# 👉 SESSION STATE INIT
if "run_reco" not in st.session_state:
    st.session_state.run_reco = False

# 👉 BUTTON
if st.button("⚡ Generate Recommendations"):
    st.session_state.run_reco = True

# 👉 MAIN LOGIC
if st.session_state.run_reco:

    with st.spinner("Generating AI recommendations..."):

        try:
            top_buy, top_sell = get_recommendations_cached(df)
        except Exception as e:
            st.error(f"Recommendation Error: {e}")
            top_buy, top_sell = pd.DataFrame(), pd.DataFrame()

    # 👉 CREATE COLUMNS (IMPORTANT: INSIDE IF)
    col1, col2 = st.columns(2)

    # ==============================
    # 🟢 BUY SIDE
    # ==============================
    with col1:
        st.markdown("### 🟢 Top BUY")

        if top_buy.empty:
            st.warning("No BUY signals")
        else:
            for _, row in top_buy.iterrows():
                st.markdown(f"""
### {row['Symbol']}

💰 **Price:** ₹{row['Current Price']}  
📈 **Predicted:** ₹{row['Predicted Price']}  
🚀 **Change:** {row['Change (%)']}%  
🎯 **Confidence:** {row['Confidence']}%

---
""")

    # ==============================
    # 🔴 SELL SIDE
    # ==============================
    with col2:
        st.markdown("### 🔴 Top SELL")

        if top_sell.empty:
            st.warning("No SELL signals")
        else:
            for _, row in top_sell.iterrows():
                st.markdown(f"""
### {row['Symbol']}

💰 **Price:** ₹{row['Current Price']}  
📉 **Predicted:** ₹{row['Predicted Price']}  
🔻 **Change:** {row['Change (%)']}%  
🎯 **Confidence:** {row['Confidence']}%

---
""")

# 👉 DEFAULT STATE
else:
    st.info("Click 'Generate Recommendations' to run AI analysis")

# ==============================
# 💼 PORTFOLIO (PRO UI)
# ==============================
st.markdown("## 💼 Portfolio Overview")

portfolio_state = st.session_state.portfolio_state
positions = portfolio_state["positions"]

if not positions:
    st.warning("No positions yet")
else:
    data = []
    total_invested = 0
    total_value = 0

    for stock, d in positions.items():
        stock_df_temp = grouped_data.get(stock)
        if stock_df_temp is None:
            continue

        price = float(stock_df_temp.iloc[-1]["Close"])

        qty = d["qty"]
        avg = d["avg_price"]

        invested = qty * avg
        value = qty * price
        pnl = value - invested

        total_invested += invested
        total_value += value

        data.append({
            "Stock": stock,
            "Qty": qty,
            "Avg Price": avg,
            "Current": price,
            "P&L": pnl
        })

    df_port = pd.DataFrame(data)

    st.dataframe(df_port, use_container_width=True)

    pnl_total = total_value - total_invested

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Invested", f"₹{round(total_invested,2)}")
    col2.metric("📊 Value", f"₹{round(total_value,2)}")
    col3.metric(
        "📈 P&L",
        f"₹{round(pnl_total,2)}",
        delta_color="normal" if pnl_total > 0 else "inverse"
    )

# ==============================
# 💰 TRADING TERMINAL (PRO)
# ==============================
st.markdown("## 💰 Trading Terminal")

portfolio_state = st.session_state.portfolio_state
current_price = float(stock_df.iloc[-1]["Close"])

col1, col2, col3 = st.columns(3)

col1.metric("💰 Balance", f"₹{round(portfolio_state['balance'],2)}")
col2.metric("📊 Price", f"₹{round(current_price,2)}")
col3.metric("📦 Holdings", len(portfolio_state["positions"]))

qty = st.slider("Quantity", 1, 100, 1)

col1, col2 = st.columns(2)

# BUY
with col1:
    if st.button("🟢 BUY", use_container_width=True):

        cost = qty * current_price

        if portfolio_state["balance"] >= cost:

            pos = portfolio_state["positions"]

            if selected_stock in pos:
                old = pos[selected_stock]
                total_qty = old["qty"] + qty

                avg = ((old["avg_price"] * old["qty"]) + (current_price * qty)) / total_qty

                pos[selected_stock] = {"qty": total_qty, "avg_price": avg}
            else:
                pos[selected_stock] = {"qty": qty, "avg_price": current_price}

            portfolio_state["balance"] -= cost
            st.success("✅ Bought Successfully")

        else:
            st.error("❌ Insufficient balance")

# SELL
with col2:
    if st.button("🔴 SELL", use_container_width=True):

        pos = portfolio_state["positions"]

        if selected_stock in pos and pos[selected_stock]["qty"] >= qty:

            portfolio_state["balance"] += qty * current_price
            pos[selected_stock]["qty"] -= qty

            if pos[selected_stock]["qty"] == 0:
                del pos[selected_stock]

            st.warning("✅ Sold Successfully")

        else:
            st.error("❌ Not enough shares")

# ==============================
# 📈 PERFORMANCE (PRO UI)
# ==============================
st.markdown("## 📈 Performance Analytics")

positions = portfolio_state["positions"]

if positions:
    total_invested = 0
    total_value = 0

    for stock, d in positions.items():
        stock_df_temp = grouped_data.get(stock)
        if stock_df_temp is None:
            continue

        price = float(stock_df_temp.iloc[-1]["Close"])

        qty = d["qty"]
        avg = d["avg_price"]

        total_invested += qty * avg
        total_value += qty * price

    pnl = total_value - total_invested
    return_pct = (pnl / total_invested) * 100 if total_invested else 0

    col1, col2 = st.columns(2)

    col1.metric("💹 Total P&L", f"₹{round(pnl,2)}")
    col2.metric("📊 Return %", f"{round(return_pct,2)}%")

    st.progress(min(max((return_pct + 50)/100, 0), 1))

else:
    st.info("No performance data yet")