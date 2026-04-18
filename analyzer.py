import pandas as pd
import numpy as np

class COTAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        if df is not None and not df.empty:
            self._preprocess()

    def _preprocess(self):
        """Prepares columns and dates."""
        # Reset index in case Streamlit cache moved our target column to the index
        self.df = self.df.reset_index()
        
        if 'Report_Date_as_YYYY-MM-DD' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Report_Date_as_YYYY-MM-DD'])
        else:
            self.df['Date'] = pd.NaT
            
        self.df = self.df.sort_values(by='Date')

    def get_assets(self):
        col_name = 'Market_and_Exchange_Names' if 'Market_and_Exchange_Names' in self.df.columns else 'Market and Exchange Names'
        if col_name in self.df.columns:
            return self.df[col_name].unique()
        # Fallback to check if any column contains 'Market'
        for c in self.df.columns:
            if 'Market' in c and 'Exchange' in c:
                return self.df[c].unique()
        return []

    def analyze_asset(self, asset_name, lookback_weeks=52):
        """Calculates Net positions and Percentiles for a specific asset (TFF Report)."""
        col_name = 'Market_and_Exchange_Names' if 'Market_and_Exchange_Names' in self.df.columns else 'Market and Exchange Names'
        
        # Fallback search
        if col_name not in self.df.columns:
            for c in self.df.columns:
                if 'Market' in c and 'Exchange' in c:
                    col_name = c
                    break
        
        if col_name not in self.df.columns:
            return None

        asset_df = self.df[self.df[col_name] == asset_name].copy()
        
        cols_to_numeric = [
            'Asset_Mgr_Positions_Long_All', 'Asset_Mgr_Positions_Short_All',
            'Lev_Money_Positions_Long_All', 'Lev_Money_Positions_Short_All',
            'Dealer_Positions_Long_All', 'Dealer_Positions_Short_All',
            'Other_Rept_Positions_Long_All', 'Other_Rept_Positions_Short_All',
            'Open_Interest_All'
        ]

        # Ensure columns exist, if not fill 0
        for col in cols_to_numeric:
            if col in asset_df.columns:
                asset_df[col] = pd.to_numeric(asset_df[col], errors='coerce').fillna(0)
            else:
                asset_df[col] = 0

        # Net Positions
        asset_df['Net Asset Mgr'] = asset_df['Asset_Mgr_Positions_Long_All'] - asset_df['Asset_Mgr_Positions_Short_All']
        asset_df['Net Lev Money'] = asset_df['Lev_Money_Positions_Long_All'] - asset_df['Lev_Money_Positions_Short_All']
        asset_df['Net Dealer'] = asset_df['Dealer_Positions_Long_All'] - asset_df['Dealer_Positions_Short_All']
        asset_df['Net Other'] = asset_df['Other_Rept_Positions_Long_All'] - asset_df['Other_Rept_Positions_Short_All']

        # Delta (Weekly Change)
        asset_df['Delta Asset Mgr'] = asset_df['Net Asset Mgr'].diff()
        asset_df['Delta Lev Money'] = asset_df['Net Lev Money'].diff()
        asset_df['Delta Dealer'] = asset_df['Net Dealer'].diff()
        asset_df['Delta Open Interest'] = asset_df['Open_Interest_All'].diff()

        # Calculate Percentile (0 to 100%)
        # Using a rolling window (e.g., 52 weeks = 1 year, 156 weeks = 3 years)
        if len(asset_df) > 10:
            rolling_min = asset_df['Net Asset Mgr'].rolling(lookback_weeks, min_periods=5).min()
            rolling_max = asset_df['Net Asset Mgr'].rolling(lookback_weeks, min_periods=5).max()
            asset_df['Percentile Asset Mgr'] = ((asset_df['Net Asset Mgr'] - rolling_min) / (rolling_max - rolling_min)) * 100
        else:
            asset_df['Percentile Asset Mgr'] = 50

        # Fill NAs
        asset_df['Percentile Asset Mgr'] = asset_df['Percentile Asset Mgr'].fillna(50)

        return asset_df

    def get_smart_money_bias(self, asset_df):
        """Calculates Market Direction Probability based on Asset Managers (Smart Money)."""
        if asset_df is None or asset_df.empty:
            return "Neutral", 0, "No data", "Neutral", "No data"

        latest = asset_df.iloc[-1]
        percentile = latest.get('Percentile Asset Mgr', 50)
        net_am = latest.get('Net Asset Mgr', 0)
        delta_am = latest.get('Delta Asset Mgr', 0)
        net_lev = latest.get('Net Lev Money', 0)
        delta_lev = latest.get('Delta Lev Money', 0)

        # Asset Manager Direction
        if net_am > 0:
            am_dir = f"ЛОНГ (+{net_am:,.0f} контрактов)"
        else:
            am_dir = f"ШОРТ ({net_am:,.0f} контрактов)"
            
        # Asset Manager Dynamics
        if delta_am > 0:
            am_dyn = f"Наращивают лонг (+{delta_am:,.0f})"
        else:
            am_dyn = f"Сокращают лонг ({delta_am:,.0f})"

        # Leveraged Funds Mood
        if net_lev > 0:
            lev_mood = f"ЛОНГ (+{net_lev:,.0f})"
        else:
            lev_mood = f"ШОРТ ({net_lev:,.0f})"
            
        if delta_lev > 0:
            lev_dyn = f"Наращивают лонг (+{delta_lev:,.0f})"
        else:
            lev_dyn = f"Сокращают лонг ({delta_lev:,.0f})"

        # Simplified Probability Model based on Percentile Constraints
        prob_long = percentile 
        # Extreme short positioning (<15%) = High reversal probability to Long
        # Extreme long positioning (>85%) = High reversal probability to Short
        
        return am_dir, am_dyn, lev_mood, lev_dyn, percentile

