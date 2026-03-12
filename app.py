import streamlit as st
import pandas as pd
import json
import os
import copy
import plotly.express as px
import plotly.graph_objects as go
from risk_engine import RiskEngine

st.set_page_config(page_title="Proprietary P&L Risk Engine", layout="wide", page_icon="📈")

st.title("📈 Proprietary P&L Risk Engine")
st.markdown("Monitor your commodity exposures, P&L attribution, and perform stress testing in real-time.")

# 1. Load Data
base_dir = os.path.dirname(os.path.abspath(__file__))
trade_book_path = os.path.join(base_dir, 'data', 'trade_book.csv')
market_data_path = os.path.join(base_dir, 'data', 'market_data.json')

with open(market_data_path, 'r') as f:
    market_data = json.load(f)
trade_book_df = pd.read_csv(trade_book_path)

# 4. Sidebar: Risk Sensitivity Slider
st.sidebar.header("Risk Sensitivity Stress Testing")
st.sidebar.markdown("Adjust the slider to simulate a sudden market price movement across all commodities.")
price_shock_pct = st.sidebar.slider("Price Shock (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)

# Apply shock to commodity prices (not FX)
stressed_market_data = copy.deepcopy(market_data)
for k, v in stressed_market_data.items():
    if k != 'GBP/USD':
        stressed_market_data[k]['price'] = v['price'] * (1 + (price_shock_pct / 100.0))

# Initialize Risk Engines
base_engine = RiskEngine(trade_book_df, market_data)
stress_engine = RiskEngine(trade_book_df, stressed_market_data)

exposure_df = base_engine.calculate_net_exposure()
_, base_summary = base_engine.calculate_mtm_pnl()
_, stress_summary = stress_engine.calculate_mtm_pnl()

# Component aggregation
total_exposure = exposure_df['Net_Flat_Exposure_MT'].sum()
total_price_pnl = base_summary['Price_Delta_PnL_GBP'].sum()
total_fx_pnl = base_summary['FX_Impact_PnL_GBP'].sum()
total_base_pnl = base_summary['Total_PnL_GBP'].sum()

total_stress_pnl = stress_summary['Total_PnL_GBP'].sum()

# 1. Executive Metrics
st.markdown("### Executive Summary")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Net Exposure (MT)", f"{total_exposure:,.0f}")
col2.metric("Price P&L (GBP)", f"£{total_price_pnl:,.0f}")
col3.metric("FX P&L (GBP)", f"£{total_fx_pnl:,.0f}")

# Stress tested PnL with delta from base
delta_pnl = total_stress_pnl - total_base_pnl
col4.metric(f"Stress Tested P&L ({price_shock_pct:+.0f}%)", f"£{total_stress_pnl:,.0f}", delta=f"£{delta_pnl:,.0f}")

st.divider()

# Charts row
chart_col1, chart_col2 = st.columns(2)

# 2. Hedge Visualization
with chart_col1:
    st.markdown("### Hedge Visualization")
    hedge_df = trade_book_df.groupby(['Commodity', 'Position_Type'])['Quantity_MT'].sum().reset_index()
    
    fig_hedge = px.bar(
        hedge_df, 
        x="Commodity", 
        y="Quantity_MT", 
        color="Position_Type", 
        barmode="group",
        color_discrete_map={
            'Physical_Long': '#2ca02c',   # Green
            'Futures_Short': '#d62728',   # Red
            'Physical_Short': '#ff7f0e',  # Orange
            'Futures_Long': '#1f77b4',    # Blue
        }
    )
    fig_hedge.update_layout(
        yaxis_title="Quantity (MT)",
        xaxis_title="Commodity",
        legend_title="Position Type",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_hedge, use_container_width=True)

# 3. P&L Attribution Waterfall
with chart_col2:
    st.markdown("### Daily P&L Bridge")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="PnL Bridge",
        orientation="v",
        measure=["relative", "relative", "total"],
        x=["Price Delta", "FX Impact", "Total MTM P&L"],
        textposition="outside",
        text=[f"£{total_price_pnl:,.0f}", f"£{total_fx_pnl:,.0f}", f"£{total_base_pnl:,.0f}"],
        y=[total_price_pnl, total_fx_pnl, total_base_pnl],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#ef553b"}},
        increasing={"marker": {"color": "#00cc96"}},
        totals={"marker": {"color": "#636efa"}}
    ))
    
    fig_waterfall.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis_title="P&L (GBP)"
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

st.divider()

# 5. Trade Ledger
st.markdown("### Trade Ledger")
st.dataframe(
    trade_book_df.style.format({
        "Quantity_MT": "{:,.0f}",
        "Contract_Price_USD": "${:,.2f}"
    }), 
    use_container_width=True
)
