# 🚀 AI Trading Dashboard with Stock Prediction & Portfolio Simulation

An intelligent stock market analysis system that combines Machine Learning, Technical Indicators, and Sentiment Analysis to predict stock prices, generate trading signals, and simulate portfolio management.

> Predict. Analyze. Trade. — All in one intelligent dashboard.

---

## 📌 Overview

This project is a full-stack AI-based trading dashboard built using Python and Streamlit. It analyzes NIFTY-50 stock data, predicts future prices using machine learning models, generates BUY/SELL signals, and allows users to simulate trading with real-time portfolio tracking.

---

## ⚙️ Features

- 📈 Stock Price Prediction using ML models
- 🧠 Smart BUY / SELL / HOLD Signal Generation
- 📰 News Sentiment Analysis
- 🔥 Smart Stock Recommendations
- 💰 Trading Terminal Simulation (₹100000 virtual balance)
- 📦 Portfolio Tracking with Avg Price & P&L
- 📊 Performance Analytics (Return, Volatility, Sharpe Ratio)
- 📉 Interactive Charts & Market Overview
- 🎨 Clean and Responsive Streamlit UI

---

## 🤖 Machine Learning Models Used

- **Gradient Boosting Regressor**
  - Used for predicting future stock prices
- **Random Forest Classifier**
  - Used for predicting market direction (BUY/SELL)

---

## 📊 Feature Engineering

- Returns (1-day, 3-day, 5-day)
- Volatility (rolling standard deviation)
- Technical Indicators:
  - RSI (Relative Strength Index)
  - MACD
  - SMA (20, 50)
  - Bollinger Bands

---

## 🧠 How It Works

1. Historical stock data is loaded and cleaned
2. Feature engineering is applied
3. ML models are trained on past data
4. Predictions are generated:
   - Next-day price
   - Market direction
5. Signals and recommendations are computed
6. Results are displayed in an interactive dashboard

---

## 💰 Trading Simulation

- Initial virtual balance: ₹100000
- Buy/Sell stocks manually
- Tracks:
  - Holdings
  - Average price
  - Profit & Loss

---

## 📊 Performance Metrics

- Annual Return
- Volatility
- Sharpe Ratio

---

## 🌐 Tech Stack

- **Frontend/UI**: Streamlit  
- **Backend**: Python  
- **ML Libraries**: Scikit-learn  
- **Data Processing**: Pandas, NumPy  
- **Visualization**: Matplotlib / Streamlit charts  

---

## 🚀 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git

# Go to project folder
cd your-repo-name

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/app.py

nifty-ai-project/
│
├── app/
│   ├── app.py
│   ├── style.css
│
├── backend/
│   ├── model_ml.py
│   ├── recommendation.py
│   ├── signal_engine.py
│   ├── portfolio.py
│   ├── indicators.py
│   ├── news_analysis.py
│
├── data/
├── models/
└── powerbi_dataset.csv

🔮 Future Enhancements

🔄 Real-time stock data integration (API)
🤖 Deep Learning (LSTM models)
📱 Mobile-friendly UI
☁️ Cloud deployment (AWS / Streamlit Cloud)
🔔 Alerts & Notifications (Telegram / Email)
💹 Auto-trading integration
⚠️ Disclaimer

This project is for educational purposes only. It does not provide financial advice or guarantee profits in stock trading.

👨‍💻 Author

Khushil Parikh 
