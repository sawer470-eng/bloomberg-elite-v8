import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap
from datetime import datetime, timedelta

from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_market_data_cached(ticker_map):
    data = []
    for name, (yf_tkr, go_tkr) in ticker_map.items():
        res = fetch_ticker_data(yf_tkr, fallback_google_ticker=go_tkr)
        if res:
            data.append({
                "Asset": name,
                "Ticker": yf_tkr,
                "Price": res['price'],
                "Change": res['change'],
                "% Change": res['pct_change'],
                "History": res['history']
            })
    return data

def get_market_data(tickers):
    return get_market_data_cached(tickers)

def render_market_data():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace;'>[MARKETS MONITOR]</h2>", unsafe_allow_html=True)
    st.write("Live quotes & Trends (Multi-Source Redundancy Active)")

    tickers = {
        "S&P 500": ("^GSPC", "SPY:NYSE"),
        "Nasdaq 100": ("^NDX", "QQQ:NASDAQ"),
        "US Dollar Index": ("DX-Y.NYB", "DXY:CUR"),
        "EUR/USD": ("EURUSD=X", "EUR-USD"),
        "Gold": ("GC=F", "GOLD:COMEX"),
        "Crude Oil": ("CL=F", "CL.1:COMEX"),
        "Bitcoin": ("BTC-USD", "BTC-USD"),
        "Ethereum": ("ETH-USD", "ETH-USD"),
        "US 10-Yr Yield": ("^TNX", "TNX:INDEXCBOE")
    }

    with st.spinner("Fetching live market data..."):
        market_data = get_market_data(tickers)
        
    if not market_data:
        st.error("Failed to load market data.")
        return

    # Render dashboard grid
    cols = st.columns(3)
    for i, item in enumerate(market_data):
        color = "#66ff00" if item["Change"] >= 0 else "#ff0033"
        arrow = "▲" if item["Change"] >= 0 else "▼"
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(textwrap.dedent(f"""
<div class="metric-card">
<div class="metric-title">{item['Asset']}</div>
<div class="metric-value">{item['Price']:.2f}</div>
<div style="color:{color}; font-size: 14px; font-family: 'JetBrains Mono';">
{arrow} {abs(item['% Change']):.2f}%
</div>
</div>
"""), unsafe_allow_html=True)
        
        with col2:
            fig = px.line(item['History'], y='Close', height=100)
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            fig.update_traces(line_color=color, line_width=2)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- S&P 500 TREEMAP ---
    st.markdown("---")
    st.markdown("### <span style='color:#45a29e'>S&P 500 SECTOR HEATMAP (WEIGHTED)</span>", unsafe_allow_html=True)
    
    sectors = {
        "Technology": ["AAPL", "MSFT", "NVDA", "AVGO"],
        "Finance": ["JPM", "BAC", "V", "MA"],
        "Healthcare": ["UNH", "JNJ", "LLY", "ABBV"],
        "Energy": ["XOM", "CVX", "COP", "SLB"],
        "Consumer": ["AMZN", "TSLA", "WMT", "HD"]
    }
    
    flat_tickers = [ticker for group in sectors.values() for ticker in group]
    
    with st.spinner("Building Treemap..."):
        try:
            # Batch download is much faster than loop
            df = yf.download(flat_tickers, period="5d", progress=False)
            
            # Build lists for DataFrame
            d_labels, d_parents, d_values, d_colors = [], [], [], []
            
            for sector, ticks in sectors.items():
                for t in ticks:
                    try:
                        prices = df['Close'][t]
                        if not prices.dropna().empty:
                            last = prices.dropna().iloc[-1]
                            prev = prices.dropna().iloc[-2]
                            pct = ((last - prev) / prev) * 100
                            
                            # Safely get Volume
                            vol = 1_000_000
                            if 'Volume' in df.columns and t in df['Volume'].columns:
                                vol_data = df['Volume'][t].dropna()
                                if not vol_data.empty and vol_data.iloc[-1] > 0:
                                    vol = vol_data.iloc[-1]
                                    
                            weight = float(vol * last)
                            if pd.isna(weight) or weight <= 0:
                                weight = 1.0
                                
                            d_labels.append(t)
                            d_parents.append(sector)
                            d_values.append(weight)
                            d_colors.append(float(pct))
                    except Exception as e:
                        pass
                        
            df_tree = pd.DataFrame({
                'Ticker': d_labels,
                'Sector': d_parents,
                'Weight': d_values,
                'Change (%)': d_colors
            })
            
            # Using Plotly Express automatically handles the roots and sizing math
            fig_tree = px.treemap(
                df_tree, 
                path=[px.Constant("S&P 500"), 'Sector', 'Ticker'], 
                values='Weight',
                color='Change (%)',
                color_continuous_scale=[[0, '#ff0033'], [0.5, '#161b22'], [1, '#66ff00']],
                color_continuous_midpoint=0
            )
            
            fig_tree.update_layout(
                height=500,
                margin=dict(t=30, l=0, r=0, b=0),
                paper_bgcolor='#000000',
                font=dict(family="monospace")
            )
            
            st.plotly_chart(fig_tree, use_container_width=True)
            
        except Exception as e:
            st.error(f"Treemap error: {e}")

