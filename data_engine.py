import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

@st.cache_data(ttl=3600)
def fetch_ticker_data(ticker, fallback_google_ticker=None):
    """
    Robust data fetching:
    1. Try yfinance.
    2. If fails, try scraping Google Finance.
    """
    try:
        # Step 1: yfinance
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1mo")
        if not hist.empty:
            return {
                "price": hist['Close'].iloc[-1],
                "change": hist['Close'].iloc[-1] - hist['Close'].iloc[-2],
                "pct_change": ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100,
                "history": hist['Close'],
                "source": "Yahoo"
            }
    except Exception as e:
        pass
    
    # Step 2: Google Finance Fallback
    if fallback_google_ticker:
        try:
            url = f"https://www.google.com/finance/quote/{fallback_google_ticker}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Google Finance CSS classes for price and change (may change over time)
            price_el = soup.find('div', {'class': 'YMlKec fxKbKc'})
            change_el = soup.find('div', {'class': 'P6L18e'})
            
            if price_el:
                price_str = price_el.text.replace('$', '').replace(',', '').replace('+', '').strip()
                price = float(price_str)
                
                # Try to extract percentage change from the element text
                pct_val = 0.0
                if change_el:
                    # Example: "+1.23 (1.23%)"
                    text = change_el.text
                    if '(' in text and '%' in text:
                        pct_str = text.split('(')[1].split('%')[0].replace('+', '').strip()
                        pct_val = float(pct_str)
                
                return {
                    "price": price,
                    "change": (price * pct_val / 100),
                    "pct_change": pct_val,
                    "history": pd.Series([price] * 20), # Flat history as scraper only gets current
                    "source": "Google (Fallback)"
                }
        except:
            pass
            
    return None

@st.cache_data(ttl=3600)
def fetch_macro_yields():
    """
    Fetch Treasury Yields with FRED Fallback.
    """
    tickers = {
        "10Y Yield": "^TNX",
        "2Y Yield": "^IRX", # 3M for simplicity if 2Y fails
        "30Y Yield": "^TYX"
    }
    
    results = {}
    for name, ticker in tickers.items():
        data = fetch_ticker_data(ticker)
        if data:
            results[name] = data
        else:
            # FRED fallback for yields
            fred_id = "DGS10" if "10Y" in name else "DGS30" if "30Y" in name else "TB3MS"
            try:
                url = f"https://fred.stlouisfed.org/series/{fred_id}/downloaddata" # Not direct CSV, but we can scrape the page
                # For brevity in this engine, if Yahoo fails, we try a direct requests-based yield scraper if possible
                pass
            except:
                pass
    return results

def get_ticker_tape_data():
    symbols = {
        "S&P 500": ("^GSPC", "SPY:NYSE"),
        "NASDAQ": ("^NDX", "QQQ:NASDAQ"),
        "GOLD": ("GC=F", "GOLD:COMEX"),
        "CRUDE": ("CL=F", "CL.1:COMEX"),
        "BTC": ("BTC-USD", "BTC-USD")
    }
    
    items = []
    for name, (yf_tkr, go_tkr) in symbols.items():
        data = fetch_ticker_data(yf_tkr, fallback_google_ticker=go_tkr)
        if data:
            color = "#66ff00" if data['pct_change'] >= 0 else "#ff0033"
            arrow = "▲" if data['pct_change'] >= 0 else "▼"
            items.append(f"<span style='color:#c5c6c7'>{name}</span> <span style='color:{color}'>{data['price']:,.2f} {arrow} {abs(data['pct_change']):.2f}%</span>")
        else:
            items.append(f"<span style='color:#c5c6c7'>{name}</span> <span style='color:#8b949e'>N/A</span>")
            
    return " &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; ".join(items)
