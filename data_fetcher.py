import cot_reports as cot
import pandas as pd
import os

class COTFetcher:
    def __init__(self):
        self.data_dir = "cot_data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_recent_data(self, report_type='traders_in_financial_futures_fut'):
        """Fetches COT data from the CFTC."""
        try:
            # For SMC we primarily use TFF (traders_in_financial_futures_fut)
            # You can also pass 'legacy_fut' or 'disaggregated_fut'
            df = cot.cot_year(year=2026, cot_report_type=report_type)
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

if __name__ == "__main__":
    fetcher = COTFetcher()
    df = fetcher.fetch_recent_data('traders_in_financial_futures_fut')
    if df is not None:
        print("Data fetched successfully!")
        print(df.columns[:20]) # Print first 20 columns to inspect TFF format
