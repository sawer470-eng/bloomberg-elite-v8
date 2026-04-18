import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def calculate_tpo(df: pd.DataFrame, tick_size: float = 0.5):
    min_p = float(df['Low'].min())
    max_p = float(df['High'].max())
    
    bins = np.arange(min_p, max_p + tick_size, tick_size)
    profile = pd.Series(0, index=bins)
    
    for _, row in df.iterrows():
        h = row['High']
        l = row['Low']
        profile.loc[(profile.index >= l) & (profile.index <= h)] += 1
        
    poc = profile.idxmax()
    total_tpos = profile.sum()
    target_tpos = total_tpos * 0.70
    
    profile_sorted = profile.copy().to_frame('count')
    profile_sorted['dist'] = abs(profile_sorted.index - poc)
    profile_sorted = profile_sorted.sort_values(by='dist')
    
    profile_sorted['cum_sum'] = profile_sorted['count'].cumsum()
    value_area = profile_sorted[profile_sorted['cum_sum'] <= target_tpos]
    
    val = value_area.index.min()
    vah = value_area.index.max()
    
    return {'poc': poc, 'val': val, 'vah': vah, 'profile': profile}

from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_tpo_raw_data_redundant(ticker, lookback, interval):
    df = yf.download(ticker, period=lookback, interval=interval, progress=False)
    if not df.empty:
        return df
    return None

def render_tpo_data():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>[VOLUME PROFILE / TPO]</h2>", unsafe_allow_html=True)
    st.write("Market Profile analysis (Point of Control & Value Area)")

    c1, c2 = st.columns([1, 2])
    with c1:
        ticker = st.text_input("Enter Ticker Symbol (e.g. SPY, QQQ, AAPL):", "SPY").upper()
        lookback = st.selectbox("Lookback Period", ["5d", "1mo", "3mo", "ytd"])
        interval = st.selectbox("Interval", ["15m", "1h", "1d"])
        
    with st.spinner("Fetching data and mapping liquidity profiles..."):
        try:
            df = get_tpo_raw_data(ticker, lookback, interval)
            if df.empty:
                st.error("No data found. Adjust ticker or intervals.")
                return
                
            # If multi-index due to yfinance quirk
            if isinstance(df.columns, pd.MultiIndex):
                # Flatten or select the ticker
                try:
                    df = df.xs(ticker, axis=1, level=1)
                except:
                    # In case it's Price as level 0
                    if ticker in df.columns.get_level_values(1):
                        df.columns = df.columns.droplevel(1)
            
            # Tick size dynamically based on price
            last_price = df['Close'].iloc[-1]
            tick_size = last_price * 0.001 # 0.1% bins
            
            tpo_data = calculate_tpo(df, tick_size=tick_size)
            poc = tpo_data['poc']
            vah = tpo_data['vah']
            val = tpo_data['val']
            profile = tpo_data['profile']
            
            # Layout
            st.markdown(f"#### Value Area Analysis for {ticker}")
            
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>VA HIGH (RESISTANCE)</div><div class='metric-value' style='color:#ff0033'>{vah:.2f}</div></div>", unsafe_allow_html=True)
            with mc2:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>POINT OF CONTROL (POC)</div><div class='metric-value' style='color:#FF9900'>{poc:.2f}</div></div>", unsafe_allow_html=True)
            with mc3:
                st.markdown(f"<div class='metric-card'><div class='metric-title'>VA LOW (SUPPORT)</div><div class='metric-value' style='color:#66ff00'>{val:.2f}</div></div>", unsafe_allow_html=True)

            # Charting
            fig = go.Figure()
            
            # Create a combined chart: Price candlestick + Horizontal TPO
            fig.add_trace(go.Bar(
                x=profile.values,
                y=profile.index,
                orientation='h',
                marker=dict(color='rgba(69, 162, 158, 0.4)'),
                name='Volume Profile'
            ))
            
            # POC Line
            fig.add_hline(y=poc, line_dash="solid", line_color="#FF9900", annotation_text="POC")
            # VAH Line
            fig.add_hline(y=vah, line_dash="dash", line_color="#ff0033", annotation_text="VAH")
            # VAL Line
            fig.add_hline(y=val, line_dash="dash", line_color="#66ff00", annotation_text="VAL")
            
            fig.update_layout(
                title="Time Price Opportunity (TPO) Distribution",
                plot_bgcolor='#0b0c10',
                paper_bgcolor='#000000',
                font=dict(color='#8b949e', family="monospace"),
                xaxis_title="Time Spent (TPOs)",
                yaxis_title="Price",
                height=600,
                xaxis=dict(showgrid=True, gridcolor='#1f2833'),
                yaxis=dict(showgrid=True, gridcolor='#1f2833')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error calculating TPO: {e}")
