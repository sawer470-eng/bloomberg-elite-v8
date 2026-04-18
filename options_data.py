import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_options_data_redundant(ticker):
    try:
        asset = yf.Ticker(ticker)
        dates = asset.options
        if not dates:
            return None, None
        exp_date = dates[0]
        chain = asset.option_chain(exp_date)
        return exp_date, chain
    except:
        return None, None

def render_options_data():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>[OPTIONS FLOW & SENTIMENT]</h2>", unsafe_allow_html=True)
    st.write("Put/Call skews and institutional positioning.")

    ticker = "SPY"
    
    with st.spinner("Fetching options chain..."):
        try:
            exp_date, chain = get_options_data_redundant(ticker)
            
            if chain is None:
                st.info("Options data not available for this session. Yahoo Finance might be rate-limited.")
                return
                
            puts = chain.puts
            calls = chain.calls
            
            put_vol = puts['volume'].sum() if 'volume' in puts.columns else 0
            call_vol = calls['volume'].sum() if 'volume' in calls.columns else 0
            
            put_oi = puts['openInterest'].sum() if 'openInterest' in puts.columns else 0
            call_oi = calls['openInterest'].sum() if 'openInterest' in calls.columns else 0
            
            # Avoid divide by zero
            pc_vol_ratio = put_vol / call_vol if call_vol > 0 else 0
            pc_oi_ratio = put_oi / call_oi if call_oi > 0 else 0
            
            # Layout
            st.markdown(f"**Nearest Expiration:** {exp_date}")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>PUT VOLUME</div><div class='metric-value'>{put_vol:,.0f}</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>CALL VOLUME</div><div class='metric-value'>{call_vol:,.0f}</div></div>", unsafe_allow_html=True)
            with c3:
                color = "#ff0033" if pc_vol_ratio > 1 else "#66ff00"
                sentiment = "BEARISH" if pc_vol_ratio > 1 else "BULLISH"
                st.markdown(f"<div class='metric-card'><div class='metric-title'>P/C VOL RATIO</div><div class='metric-value' style='color:{color}'>{pc_vol_ratio:.2f}</div><div style='color:{color}; font-size:12px;'>{sentiment}</div></div>", unsafe_allow_html=True)
            with c4:
                oi_color = "#ff0033" if pc_oi_ratio > 1.2 else "#66ff00"
                oi_sentiment = "BEARISH EXTREME" if pc_oi_ratio > 1.2 else "NORMAL/BULLISH"
                st.markdown(f"<div class='metric-card'><div class='metric-title'>P/C OI RATIO</div><div class='metric-value' style='color:{oi_color}'>{pc_oi_ratio:.2f}</div><div style='color:{oi_color}; font-size:12px;'>{oi_sentiment}</div></div>", unsafe_allow_html=True)
                
            # Chart
            fig = go.Figure()
            fig.add_trace(go.Bar(x=calls['strike'], y=calls['volume'], name='Call Volume', marker_color='#66ff00'))
            fig.add_trace(go.Bar(x=puts['strike'], y=puts['volume'], name='Put Volume', marker_color='#ff0033'))
            
            fig.update_layout(
                title="Options Volume by Strike",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#8b949e', family="monospace"),
                barmode='group',
                xaxis_title="Strike Price",
                yaxis_title="Volume",
                xaxis=dict(showgrid=True, gridcolor='rgba(69, 162, 158, 0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(69, 162, 158, 0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error fetching options: {e}")
