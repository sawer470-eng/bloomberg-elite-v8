import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_valuation_info_redundant(ticker):
    # Try Yahoo first for fundamental data
    try:
        asset = yf.Ticker(ticker)
        if asset.info and 'currentPrice' in asset.info:
            return asset.info
    except:
        pass
        
    # Fallback to data engine
    res = fetch_ticker_data(ticker)
    if res:
        return {'currentPrice': res['price'], 'shortName': ticker}
    return None

def render_fair_value_data():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>[FAIR VALUE & ANALYST CONSENSUS]</h2>", unsafe_allow_html=True)
    st.write("Compare current market price against institutional target ranges.")

    c1, c2 = st.columns([1, 2])
    with c1:
        ticker = st.text_input("Enter Ticker Symbol (e.g. MSFT, AAPL, NVDA):", "MSFT").upper()
        
    with st.spinner(f"Analyzing intrinsic valuation for {ticker}..."):
        try:
            info = get_valuation_info_redundant(ticker)
            
            if not info or 'currentPrice' not in info:
                st.error("No valuation data found. Ensure it is a valid stock ticker.")
                return
                
            current = info.get('currentPrice', 0)
            low = info.get('targetLowPrice', current)
            mean = info.get('targetMeanPrice', current)
            high = info.get('targetHighPrice', current)
            
            # Layout Multiples
            st.markdown("#### Valuation Multiples")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                pe = info.get('trailingPE', 'N/A')
                st.markdown(f"<div class='metric-card'><div class='metric-title'>TRAILING P/E</div><div class='metric-value'>{pe}</div></div>", unsafe_allow_html=True)
            with m2:
                fwd_pe = info.get('forwardPE', 'N/A')
                st.markdown(f"<div class='metric-card'><div class='metric-title'>FORWARD P/E</div><div class='metric-value'>{fwd_pe}</div></div>", unsafe_allow_html=True)
            with m3:
                pb = info.get('priceToBook', 'N/A')
                st.markdown(f"<div class='metric-card'><div class='metric-title'>PRICE TO BOOK</div><div class='metric-value'>{pb}</div></div>", unsafe_allow_html=True)
            with m4:
                rec = str(info.get('recommendationKey', 'N/A')).upper()
                color = "#66ff00" if "BUY" in rec else "#ff0033" if "SELL" in rec else "#FF9900"
                st.markdown(f"<div class='metric-card'><div class='metric-title'>CONSENSUS</div><div class='metric-value' style='color:{color}'>{rec}</div></div>", unsafe_allow_html=True)

            # Target Price visualization
            st.markdown("#### Analyst Target Price Range (Next 12M)")
            
            # Simple horizontal box/whisker plot using Scatter
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=[low, mean, high],
                y=["Target", "Target", "Target"],
                mode="markers+lines",
                name="Analyst Range",
                line=dict(color="#8b949e", width=4),
                marker=dict(symbol="line-ns", size=20, color="#c5c6c7")
            ))
            
            # Current Price Marker
            fig.add_trace(go.Scatter(
                x=[current],
                y=["Target"],
                mode="markers+text",
                name="Current Price",
                marker=dict(symbol="star", size=20, color="#FF9900"),
                text=[f"Current: {current}"],
                textposition="bottom center"
            ))
            
            fig.update_layout(
                height=300,
                plot_bgcolor='#0b0c10',
                paper_bgcolor='#000000',
                font=dict(color='#8b949e', family="monospace"),
                xaxis=dict(showgrid=True, gridcolor='#1f2833'),
                yaxis=dict(showgrid=False, visible=False),
                showlegend=False,
                margin=dict(t=20, b=20, l=10, r=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Fundamental context
            st.markdown(
                "<div style='font-size:12px; color:#8b949e;'>"
                "<b>Forward P/E vs Trailing P/E:</b> If Forward is lower than Trailing, earnings are expected to grow.<br>"
                "<b>Note:</b> Targets are aggregate Wall Street estimates. Intrinsic tracking helps identify severe market overreactions."
                "</div>", unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error fetching Fair Value data: {e}")
