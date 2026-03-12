# Proprietary Commodity P&L Risk Engine

A professional-grade, interactive Risk and Mark-to-Market (MTM) P&L attribution engine for agricultural commodities. Built with Python and Streamlit, this tool accurately nets physical and paper exposures, dynamically fetches live market data, and visualizes P&L components (Price vs. FX) and stress test scenarios.

## 🚀 Features

*   **Dynamic Exposure Netting**: Automatically parses a merchandising trade book of `Physical` (Long/Short) and `Futures` (Long/Short) positions, intelligently netting them to calculate the true "Net Flat Price Exposure" in Metric Tons (MT).
*   **Precision MTM Attribution**: Isolates and attributes daily P&L into distinct, actionable buckets:
    *   **Price Delta P&L**: Driven strictly by the underlying commodity price movements (incorporating unit conversions from Cents/Bushel to USD/MT).
    *   **FX Impact P&L**: Driven by currency fluctuations (e.g., GBP/USD) between the execution date and the current valuation date.
*   **Live Market Data Integration**: Utilizes the `yfinance` API to fetch real-time closing prices for Corn (ZC=F), Soybeans (ZS=F), and foreign exchange rates.
*   **Interactive Streamlit Dashboard**: A sleek, dark-mode financial dashboard featuring:
    *   **Executive Metrics**: Instant visibility into total net exposure and P&L breakdowns.
    *   **Hedge Visualization**: Plotly grouped bar charts visualizing the relationship between physical assets and paper hedges.
    *   **Daily P&L Bridge**: A standard financial Waterfall chart visualizing the additive step-up from Price Delta to FX Impact.
    *   **Live Stress Testing**: A responsive sidebar slider enabling instant "-50% to +50%" price shocks to evaluate tail risk on the portfolio's MTM value.

## 🛠 Tech Stack

*   **Core Logic**: Python, Pandas
*   **Frontend UI**: Streamlit
*   **Data Visualization**: Plotly (`plotly.express`, `plotly.graph_objects`)
*   **Market Data Connector**: `yfinance`

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
```

## ⚙️ How to Run Locally

1. **Clone the repository** (or navigate to the project directory).
2. **Set up a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Generate data and fetch live prices**:
   ```bash
   python init_risk_data.py
   ```
5. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```

## 💼 Use Case

This engine demonstrates the ability to translate complex financial and physical merchandising risk concepts (net exposure, FX impact, P&L bridges, stress testing) into clean algorithmic logic and highly readable, interactive software.
