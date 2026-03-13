# Proprietary Commodity P&L Risk Engine

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://commodity-pnl-risk-engine-moberick.streamlit.app)

**🔗 [Live Interactive Risk Dashboard](https://commodity-pnl-risk-engine-moberick.streamlit.app)**

## Executive Summary
A professional-grade, interactive Risk and Mark-to-Market (MTM) P&L attribution engine for agricultural commodities. Built with Python and Streamlit, this tool accurately nets physical and paper exposures, dynamically fetches live market data, and visualizes P&L components (Price vs. FX) and stress test scenarios.

## 🚀 Features
* **Dynamic Exposure Netting**: Automatically parses a merchandising trade book of `Physical` and `Futures` positions, netting them to calculate the true **'Net Flat Price Exposure'** in Metric Tons (MT).
* **Precision MTM Attribution**: Isolates and attributes daily P&L into distinct, actionable buckets, successfully isolating drivers such as **Price Delta** and **Forex (FX) fluctuations**.
* **Live Market Data Integration**: Utilizes the `yfinance` API to fetch real-time closing prices for Corn (ZC=F), Soybeans (ZS=F), and foreign exchange rates.
* **Interactive Streamlit Dashboard**: A sleek financial dashboard featuring:
    * **Executive Metrics**: Instant visibility into total net exposure and P&L breakdowns.
    * **Hedge Visualization**: Plotly grouped bar charts visualizing the relationship between physical assets and paper hedges.
    * **Daily P&L Bridge**: A standard financial Waterfall chart visualizing the additive step-up from Price Delta to FX Impact.
    * **Live Stress Testing**: A responsive sidebar slider enabling instant price shocks to evaluate **calculated risk appetite**.

## 🛠 Tech Stack
* **Core Logic**: Python (Pandas/NumPy)
* **Frontend UI**: Streamlit
* **Data Visualization**: Plotly (`plotly.express`, `plotly.graph_objects`)
* **Market Data Connector**: `yfinance`

## 📁 Project Structure
```text
commodity_pnl_risk_engine/
├── app.py                 # Streamlit frontend dashboard
├── risk_engine.py         # Core Python P&L and netting calculations class
├── init_risk_data.py      # Script to generate synthetic trade book & fetch market data
├── requirements.txt       # Python dependencies
└── data/
    ├── trade_book.csv     # Synthesized physical & futures positions
    └── market_data.json   # Cached live market data via Yahoo Finance
