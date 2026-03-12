import os
import json
from datetime import datetime
import pandas as pd
import yfinance as yf

def main():
    # 1. Create a /data directory in the current working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"Ensured data directory exists at: {data_dir}")

    # 2. Generate a trade_book.csv representing a merchandising position
    # The positions below show physical exposure partially or fully offset by futures
    trades = [
        # Corn Positions
        {'Trade_ID': 'TRD-1001', 'Commodity': 'Corn', 'Position_Type': 'Physical_Long', 'Quantity_MT': 5000, 'Contract_Price_USD': 175.50},
        {'Trade_ID': 'TRD-1002', 'Commodity': 'Corn', 'Position_Type': 'Futures_Short', 'Quantity_MT': 4000, 'Contract_Price_USD': 178.00},
        {'Trade_ID': 'TRD-1003', 'Commodity': 'Corn', 'Position_Type': 'Physical_Long', 'Quantity_MT': 2500, 'Contract_Price_USD': 172.00},
        {'Trade_ID': 'TRD-1004', 'Commodity': 'Corn', 'Position_Type': 'Futures_Short', 'Quantity_MT': 3000, 'Contract_Price_USD': 176.50},
        
        # Soybeans Positions
        {'Trade_ID': 'TRD-2001', 'Commodity': 'Soybeans', 'Position_Type': 'Physical_Short', 'Quantity_MT': 3000, 'Contract_Price_USD': 455.00},
        {'Trade_ID': 'TRD-2002', 'Commodity': 'Soybeans', 'Position_Type': 'Futures_Long', 'Quantity_MT': 2500, 'Contract_Price_USD': 450.00},
        {'Trade_ID': 'TRD-2003', 'Commodity': 'Soybeans', 'Position_Type': 'Physical_Long', 'Quantity_MT': 8000, 'Contract_Price_USD': 445.00},
        {'Trade_ID': 'TRD-2004', 'Commodity': 'Soybeans', 'Position_Type': 'Futures_Short', 'Quantity_MT': 6500, 'Contract_Price_USD': 448.50},
    ]

    df_trades = pd.DataFrame(trades)
    trade_book_path = os.path.join(data_dir, 'trade_book.csv')
    df_trades.to_csv(trade_book_path, index=False)
    print(f"Generated {len(df_trades)} trades and saved to {trade_book_path}")

    # 3. Use yfinance to fetch the current price
    print("\nFetching market data from Yahoo Finance...")
    tickers = {
        'Corn': 'ZC=F',
        'Soybeans': 'ZS=F',
        'GBP/USD': 'GBPUSD=X' # Could also use GBX for pennies if needed, but standard GBP/USD works
    }
    
    market_snaps = {}
    for name, ticker_symbol in tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Get the latest daily price
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                market_snaps[name] = {
                    'symbol': ticker_symbol,
                    'price': round(current_price, 4),
                    'timestamp': datetime.now().isoformat()
                }
                print(f"Successfully fetched {name} ({ticker_symbol}): {market_snaps[name]['price']}")
            else:
                print(f"Warning: Could not fetch data for {name} ({ticker_symbol}) - empty data returned.")
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # Save to market_data.json
    market_data_path = os.path.join(data_dir, 'market_data.json')
    with open(market_data_path, 'w') as f:
        json.dump(market_snaps, f, indent=4)
    print(f"Saved market snaps to {market_data_path}")

    # 4. Print a summary of the generated trade book to the console
    print("\n" + "="*40)
    print("TRADE BOOK SUMMARY")
    print("="*40)
    summary_df = df_trades.groupby(['Commodity', 'Position_Type'])[['Quantity_MT']].sum().reset_index()
    print(summary_df.to_string(index=False))
    
    print("\nNet Exposure by Commodity (MT)")
    print("-" * 30)
    for commodity in ['Corn', 'Soybeans']:
        commodity_trades = df_trades[df_trades['Commodity'] == commodity]
        phys_long = commodity_trades[commodity_trades['Position_Type'] == 'Physical_Long']['Quantity_MT'].sum()
        phys_short = commodity_trades[commodity_trades['Position_Type'] == 'Physical_Short']['Quantity_MT'].sum()
        fut_long = commodity_trades[commodity_trades['Position_Type'] == 'Futures_Long']['Quantity_MT'].sum()
        fut_short = commodity_trades[commodity_trades['Position_Type'] == 'Futures_Short']['Quantity_MT'].sum()
        
        net_physical = phys_long - phys_short
        net_futures = fut_long - fut_short
        net_flat = net_physical + net_futures
        print(f"{commodity}:")
        print(f"  Net Physical: {net_physical}")
        print(f"  Net Futures:  {net_futures}")
        print(f"  Net Flat:     {net_flat}")

if __name__ == "__main__":
    main()
