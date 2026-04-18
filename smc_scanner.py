import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import textwrap

def find_fvgs(df):
    fvgs = []
    # FVG is a 3-candle pattern
    for i in range(2, len(df)):
        # Bullish FVG
        if df['Low'].iloc[i] > df['High'].iloc[i-2]:
            fvgs.append({
                'type': 'Bullish',
                'top': df['Low'].iloc[i],
                'bottom': df['High'].iloc[i-2],
                'date': df.index[i-1]
            })
        # Bearish FVG
        if df['High'].iloc[i] < df['Low'].iloc[i-2]:
            fvgs.append({
                'type': 'Bearish',
                'top': df['Low'].iloc[i-2],
                'bottom': df['High'].iloc[i],
                'date': df.index[i-1]
            })
    return fvgs

def find_bos(df):
    # Simplified BOS logic: close above/below previous high/low
    # Using 10-period rolling high/low as structure
    df['PrevHigh'] = df['High'].shift(1).rolling(10).max()
    df['PrevLow'] = df['Low'].shift(1).rolling(10).min()
    
    bos_events = []
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['PrevHigh'].iloc[i]:
            bos_events.append({'type': 'BOS Bullish', 'price': df['Close'].iloc[i], 'date': df.index[i]})
        elif df['Close'].iloc[i] < df['PrevLow'].iloc[i]:
            bos_events.append({'type': 'BOS Bearish', 'price': df['Close'].iloc[i], 'date': df.index[i]})
    return bos_events

from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_smc_data_redundant(asset, period, interval):
    # Try Yahoo
    df = yf.download(asset, period=period, interval=interval, progress=False)
    if not df.empty:
        return df
    return None

def render_smc_scanner():
    st.markdown(textwrap.dedent("""
        <h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>
            [SMC STRUCTURE SCANNER: ELITE V3]
        </h2>
    """), unsafe_allow_html=True)
    
    asset = st.selectbox("Select Asset", ["EURUSD=X", "GBPUSD=X", "GC=F", "NQ=F", "BTC-USD"], index=0)
    timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"], index=0)
    
    with st.spinner(f"Scanning market structure for {asset}..."):
        period = "60d" if timeframe in ["1h", "4h"] else "1y"
        df = get_smc_data(asset, period, timeframe)
        
        if df.empty:
            st.warning("No data found.")
            return

        # Flatten columns if MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        fvgs = find_fvgs(df)
        bos_events = find_bos(df)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Latest Fair Value Gaps (FVG)")
            if fvgs:
                for fvg in fvgs[-5:]:
                    color = "#66ff00" if fvg['type'] == 'Bullish' else "#ff0033"
                    st.markdown(f"""
                        <div class="metric-card" style="padding: 10px; border-left: 4px solid {color}">
                            <div style="font-size: 12px; color: #8b949e">{fvg['date'].strftime('%Y-%m-%d %H:%M')}</div>
                            <div style="font-weight: bold; color: {color}">{fvg['type']} FVG</div>
                            <div>Range: {fvg['bottom']:.5f} - {fvg['top']:.5f}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No FVG detected in recent range.")
        
        with c2:
            st.markdown("#### Market Structure Breaks (BOS)")
            if bos_events:
                for bos in bos_events[-5:]:
                    color = "#66ff00" if "Bullish" in bos['type'] else "#ff0033"
                    st.markdown(f"""
                        <div class="metric-card" style="padding: 10px; border-left: 4px solid {color}">
                            <div style="font-size: 12px; color: #8b949e">{bos['date'].strftime('%Y-%m-%d %H:%M')}</div>
                            <div style="font-weight: bold; color: {color}">{bos['type']}</div>
                            <div>Price: {bos['price']:.5f}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.markdown("#### Structure Visualization")
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        name='Price')])
        
        # Highlight FVG as boxes
        for fvg in fvgs[-3:]:
            fig.add_shape(type="rect",
                x0=fvg['date'], x1=df.index[-1],
                y0=fvg['bottom'], y1=fvg['top'],
                fillcolor="green" if fvg['type'] == 'Bullish' else "red",
                opacity=0.2, line_width=0)

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
