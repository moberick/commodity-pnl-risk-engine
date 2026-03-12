import pandas as pd
import json

class RiskEngine:
    def __init__(self, trade_book_df, market_data):
        """
        Initializes the Risk Engine with trade data and market snapshots.
        """
        self.trades = trade_book_df
        self.market_data = market_data
        
    @classmethod
    def from_files(cls, trade_book_path, market_data_path):
        """
        Helper method to instantiate from CSV and JSON files.
        """
        trades = pd.read_csv(trade_book_path)
        with open(market_data_path, 'r') as f:
            market_data = json.load(f)
        return cls(trades, market_data)

    def calculate_net_exposure(self):
        """
        Nets physical against paper to find the 'Net Flat Price Exposure' in MT.
        Returns a summarized DataFrame.
        """
        # Map positions to multipliers
        direction_map = {
            'Physical_Long': 1,
            'Physical_Short': -1,
            'Futures_Long': 1,
            'Futures_Short': -1
        }
        
        df = self.trades.copy()
        df['Direction'] = df['Position_Type'].map(direction_map)
        df['Signed_Quantity_MT'] = df['Quantity_MT'] * df['Direction']
        
        # We can group by Commodity
        exposure_summary = []
        for commodity, group in df.groupby('Commodity'):
            phys_mask = group['Position_Type'].str.contains('Physical')
            paper_mask = group['Position_Type'].str.contains('Futures')
            
            net_physical = group.loc[phys_mask, 'Signed_Quantity_MT'].sum()
            net_paper = group.loc[paper_mask, 'Signed_Quantity_MT'].sum()
            net_flat = net_physical + net_paper
            
            exposure_summary.append({
                'Commodity': commodity,
                'Net_Physical_MT': net_physical,
                'Net_Paper_MT': net_paper,
                'Net_Flat_Exposure_MT': net_flat
            })
            
        return pd.DataFrame(exposure_summary)

    def _get_current_price_usd_mt(self, commodity):
        """
        Helper method to get the current market price and convert it to USD per Metric Ton (MT).
        CBOT agricultural futures are usually quoted in US Cents per Bushel.
        Conversion factors:
        Corn:     1 MT = ~39.368 bushels
        Soybeans: 1 MT = ~36.7437 bushels
        """
        price_data = self.market_data.get(commodity, {})
        raw_price = price_data.get('price', 0.0)
        
        if raw_price == 0.0:
            return 0.0
            
        if commodity == 'Corn':
            # Raw price is cents/bushel. Convert to USD/MT.
            return (raw_price / 100.0) * 39.368
        elif commodity == 'Soybeans':
            # Raw price is cents/bushel. Convert to USD/MT.
            return (raw_price / 100.0) * 36.7437
        else:
            return raw_price
            
    def calculate_mtm_pnl(self, historical_gbp_usd=1.35):
        """
        Calculates Mark-to-Market (MTM) P&L, isolating:
        - Price Delta P&L
        - FX Impact P&L
        
        Args:
            historical_gbp_usd: An assumed FX rate at the time of trade execution. 
                                Since it's not in the trade book, we use this to calculate FX impact.
                                
        Returns:
            trade_level_df: Detailed PnL per trade
            summary_df: Aggregated PnL by commodity
        """
        df = self.trades.copy()
        
        direction_map = {
            'Physical_Long': 1,
            'Physical_Short': -1,
            'Futures_Long': 1,
            'Futures_Short': -1
        }
        df['Direction'] = df['Position_Type'].map(direction_map)
        
        current_fx = self.market_data.get('GBP/USD', {}).get('price', 1.30)
        
        pnl_records = []
        
        for idx, row in df.iterrows():
            commodity = row['Commodity']
            
            # Use helper to get properly converted USD/MT price to match contract
            current_price_usd_mt = self._get_current_price_usd_mt(commodity)
            
            qty = row['Quantity_MT']
            contract_price = row['Contract_Price_USD']
            direction = row['Direction']
            
            # --- 1. Price Delta P&L ---
            # Formula: Quantity * (Current Price - Contract Price) * Direction
            # Ensures Short positions profit when current price < contract price
            # Example: Short (-1) * (180 - 185) = +5 Profit
            delta_pnl_usd = qty * (current_price_usd_mt - contract_price) * direction
            
            # We translate the trade's price delta P&L to GBP using the *current* FX rate.
            price_delta_pnl_gbp = delta_pnl_usd / current_fx if current_fx else 0
            
            # --- 2. FX Impact P&L ---
            # Initial Notional Principal Value in USD
            principal_usd = qty * contract_price * direction
            
            # The difference in the GBP value of the USD principal caused purely by the FX rate change
            fx_impact_pnl_gbp = principal_usd * ((1 / current_fx) - (1 / historical_gbp_usd))
            
            total_pnl_gbp = price_delta_pnl_gbp + fx_impact_pnl_gbp
            
            pnl_records.append({
                'Trade_ID': row['Trade_ID'],
                'Commodity': commodity,
                'Position_Type': row['Position_Type'],
                'Quantity_MT': qty,
                'Contract_Price_USD': contract_price,
                'Current_Price_USD': current_price_usd_mt,
                'Price_Delta_PnL_USD': delta_pnl_usd,
                'Price_Delta_PnL_GBP': price_delta_pnl_gbp,
                'FX_Impact_PnL_GBP': fx_impact_pnl_gbp,
                'Total_PnL_GBP': total_pnl_gbp
            })
            
        pnl_df = pd.DataFrame(pnl_records)
        
        # Summarize by commodity using sum
        summary_df = pnl_df.groupby('Commodity').agg({
            'Price_Delta_PnL_USD': 'sum',
            'Price_Delta_PnL_GBP': 'sum',
            'FX_Impact_PnL_GBP': 'sum',
            'Total_PnL_GBP': 'sum'
        }).reset_index()
        
        return pnl_df, summary_df

if __name__ == "__main__":
    import os
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trade_book_path = os.path.join(base_dir, 'data', 'trade_book.csv')
    market_data_path = os.path.join(base_dir, 'data', 'market_data.json')
    
    # Initialize Engine
    engine = RiskEngine.from_files(trade_book_path, market_data_path)
    
    print("="*60)
    print("NET EXPOSURE SUMMARY")
    print("="*60)
    exposure_summary = engine.calculate_net_exposure()
    print(exposure_summary.to_string(index=False))
    
    print("\n" + "="*60)
    print("MARK-TO-MARKET P&L ATTRIBUTION (GBP)")
    print("="*60)
    
    # Run PnL using a hypothetical historical execution GBP/USD rate
    trade_level_pnl, commodity_summary = engine.calculate_mtm_pnl(historical_gbp_usd=1.35)
    
    # Format for clean display
    pd.options.display.float_format = '{:,.2f}'.format
    
    print("--- Commodity Summary ---")
    print(commodity_summary.to_string(index=False))
