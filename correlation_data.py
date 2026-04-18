import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_correlation_data_redundant(tickers_dict):
    close_prices = {}
    for name, (yf_tkr, go_tkr) in tickers_dict.items():
        res = fetch_ticker_data(yf_tkr, fallback_google_ticker=go_tkr)
        if res:
            close_prices[name] = res['history']
    return pd.DataFrame(close_prices)

def render_correlation_matrix():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 1px solid #30363d; padding-bottom:10px;'>[ASSET CORRELATION MATRIX]</h2>", unsafe_allow_html=True)
    st.write("Cross-Asset Correlation Heatmap (Trailing 90 Days)")

    tickers_dict = {
        "DXY Index": ("DX-Y.NYB", "DXY:CUR"),
        "EUR/USD": ("EURUSD=X", "EUR-USD"),
        "GBP/USD": ("GBPUSD=X", "GBP-USD"),
        "GER 40": ("^GDAXI", "DAX:INDEXDB"),
        "S&P 500": ("SPY", "SPY:NYSE"),
        "Nasdaq": ("QQQ", "QQQ:NASDAQ"),
        "Gold": ("GLD", "GLD:NYSEARCA"),
        "Crude Oil": ("USO", "USO:NYSEARCA"),
        "Treasuries": ("TLT", "TLT:NASDAQ"),
        "Bitcoin": ("BTC-USD", "BTC-USD")
    }
    
    with st.spinner("Calculating full correlation matrix..."):
        try:
            df_hist = get_correlation_data_redundant(tickers_dict)
            
            if df_hist.empty:
                st.error("Failed to download correlation data. Financial markets might be closed or API limits reached.")
                return
                
            close_prices = df['Close']
            
            # Map column names to readable names
            close_prices = close_prices.rename(columns={v: k for k, v in tickers_dict.items()})
            
            # Calculate daily percentage returns
            returns = close_prices.pct_change().dropna()
            
            # Calculate Pearson correlation matrix
            corr = returns.corr()
            
            # Plot Heatmap
            fig = px.imshow(
                corr,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale=[[0, '#ff0033'], [0.5, '#161b22'], [1, '#66ff00']],
                zmin=-1, zmax=1
            )
            
            fig.update_layout(
                height=600,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8b949e', family="monospace"),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Precision Correlation Table")
            st.dataframe(corr.style.background_gradient(cmap='RdYlGn', axis=None).format("{:.4f}"), use_container_width=True)
            
            st.markdown(
                "<div style='font-size:12px; color:#8b949e; margin-top:20px;'>"
                "<b>Institutional Insight:</b> Trading EURUSD often requires tracking its inverse correlation with the DXY. "
                "The GER 40 (DAX) is highly sensitive to Euro strength and US Index (SPY) sentiment. "
                "Smart Money uses these 'Intermarket' links to confirm trends."
                "</div>", unsafe_allow_html=True
            )
                
        except Exception as e:
            st.error(f"Error computing matrix: {e}")
