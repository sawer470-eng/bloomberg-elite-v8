import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import textwrap

from data_engine import fetch_ticker_data

@st.cache_data(ttl=3600)
def get_macro_data():
    tickers = {
        "3M Yield": ("^IRX", "TY00:INDEXBM"), # Google handles these differently, might need specific codes
        "5Y Yield": ("^FVX", "FVX:INDEXCBOE"),
        "10Y Yield": ("^TNX", "TNX:INDEXCBOE"),
        "30Y Yield": ("^TYX", "TYX:INDEXCBOE"),
        "VIX (Volatility)": ("^VIX", "VIX:INDEXCBOE"),
        "DXY (USD Index)": ("DX-Y.NYB", "DXY:CUR")
    }
    
    results = {}
    for name, (yf_tkr, go_tkr) in tickers.items():
        data = fetch_ticker_data(yf_tkr, fallback_google_ticker=go_tkr)
        if data:
            current = data['price']
            history = data['history']
            month_ago = history.iloc[0] if not history.empty else current * 0.98
            results[name] = {
                "current": current,
                "change": data['change'],
                "month_ago": month_ago
            }
    return results

def render_macro_data():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 1px solid #30363d; padding-bottom:10px;'>[MACRO & RATES]</h2>", unsafe_allow_html=True)
    
    with st.spinner("Loading Macro Data..."):
        data = get_macro_data()
        
    if not data:
        st.error("Failed to load macro data.")
        return

    # LAYOUT ROW 1: CARDS
    cols = st.columns(len(data))
    for col, (name, metrics) in zip(cols, data.items()):
        val = metrics['current']
        chg = metrics['change']
        color = "#ff0033" if chg < 0 else "#66ff00"
        arrow = "▲" if chg >= 0 else "▼"
        suffix = " pts" if name in ["VIX (Volatility)", "DXY (USD Index)"] else "%"
        
        html = f"""
        <div class="metric-card">
            <div class="metric-title">{name}</div>
            <div class="metric-value">{val:.2f}{suffix}</div>
            <div style="color: {color}; font-size: 12px;">{arrow} {abs(chg):.2f} (Daily)</div>
        </div>
        """
        col.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # LAYOUT ROW 2: SPREADS & CHARTS
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### KEY SPREADS & INDICATORS")
        
        y10 = data.get("10Y Yield", {}).get("current", 0)
        y3m = data.get("3M Yield", {}).get("current", 0)
        spread_10y_3m = y10 - y3m
        
        status_color = "#ff0033" if spread_10y_3m < 0 else "#66ff00"
        status_text = "INVERTED (RECESSION WARNING)" if spread_10y_3m < 0 else "NORMAL / STEEPENING"
        
        html_spreads = textwrap.dedent(f"""<div class="metric-card" style="height: 350px;">
<div style="margin-bottom: 20px;">
<div class="metric-title">10Y - 3M SPREAD</div>
<div class="metric-value">{spread_10y_3m:.2f}%</div>
<div style="color: {status_color}; font-size: 14px; margin-top: 5px;">{status_text}</div>
</div>
<div style="margin-bottom: 20px;">
<div class="metric-title">VIX LEVEL ALERT</div>
<div style="color: {'#ff0033' if data.get('VIX (Volatility)', {}).get('current', 0) > 20 else '#66ff00'}; font-size: 18px;">
{'HIGH VOLATILITY (>20)' if data.get('VIX (Volatility)', {}).get('current', 0) > 20 else 'LOW/NORMAL VOLATILITY'}
</div>
</div>
<hr style="border-color: #30363d;">
<div style="color: #8b949e; font-size: 11px;">
Fed Funds futures and OIS pricing typically mirror the 3M/6M tenor. 
An inverted 10Y-3M spread has historically preceded every US recession since 1970.
</div>
</div>""")
        st.markdown(html_spreads, unsafe_allow_html=True)
        
    with col2:
        names = ["3M Yield", "5Y Yield", "10Y Yield", "30Y Yield"]
        x_labels = ["3 Month", "5 Year", "10 Year", "30 Year"]
        y_current = [data.get(n, {}).get("current", 0) for n in names]
        y_month = [data.get(n, {}).get("month_ago", 0) for n in names]
        
        fig = go.Figure()
        
        # Current Curve
        fig.add_trace(go.Scatter(
            x=x_labels, y=y_current, 
            mode='lines+markers', 
            marker=dict(size=10, color='#FF9900'),
            line=dict(color='#FF9900', width=3),
            name="Current"
        ))
        
        # 1 Month Ago Curve
        fig.add_trace(go.Scatter(
            x=x_labels, y=y_month, 
            mode='lines+markers', 
            marker=dict(size=8, color='#8b949e'),
            line=dict(color='#8b949e', width=2, dash='dash'),
            name="1 Month Ago"
        ))

        fig.update_layout(
            title=dict(text="US TREASURY YIELD CURVE", font=dict(color="#c5c6c7", size=16)),
            height=350,
            plot_bgcolor='#0b0c10',
            paper_bgcolor='#0b0c10',
            margin=dict(l=0, r=0, t=40, b=0),
            font=dict(color='#8b949e', family="monospace"),
            yaxis_title="Yield (%)",
            xaxis_title="Maturity",
            xaxis=dict(showgrid=True, gridcolor='#1f2833'),
            yaxis=dict(showgrid=True, gridcolor='#1f2833'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    # ECONOMIC CALENDAR
    st.markdown("---")
    st.markdown("#### UPCOMING MACRO EVENTS (EST)")
    
    events = [
        {"Date": "2026-05-01 14:00", "Event": "FOMC Interest Rate Decision", "Impact": "HIGH", "Prev": "4.50%"},
        {"Date": "2026-05-03 08:30", "Event": "Non Farm Payrolls (NFP)", "Impact": "HIGH", "Prev": "210K"},
        {"Date": "2026-05-13 08:30", "Event": "Core CPI (MoM)", "Impact": "HIGH", "Prev": "0.3%"},
        {"Date": "2026-05-14 08:30", "Event": "Retail Sales (MoM)", "Impact": "MED", "Prev": "0.4%"},
        {"Date": "2026-05-21 10:00", "Event": "Existing Home Sales", "Impact": "MED", "Prev": "4.21M"},
    ]
    
    df_events = pd.DataFrame(events)
    
    def highlight_impact(val):
        color = '#ff0033' if val == 'HIGH' else '#FF9900' if val == 'MED' else '#c5c6c7'
        return f'color: {color}; font-weight: bold;'
        
    st.dataframe(
        df_events.style.map(highlight_impact, subset=['Impact']),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("#### [CENTRAL BANK TRACKER: G7 RATES]")
    
    banks = {
        "FED (USA)": {"rate": "5.50%", "next": "2026-05-01", "sentiment": "Hawkish"},
        "ECB (EU)": {"rate": "4.50%", "next": "2026-06-06", "sentiment": "Neutral"},
        "BoE (UK)": {"rate": "5.25%", "next": "2026-05-09", "sentiment": "Dovish"},
        "BoJ (Japan)": {"rate": "0.10%", "next": "2026-04-26", "sentiment": "Pivot"}
    }
    
    bcols = st.columns(len(banks))
    for i, (name, info) in enumerate(banks.items()):
        with bcols[i]:
            st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="font-size: 11px; color: #45a29e;">{name}</div>
                    <div style="font-size: 20px; font-weight: bold;">{info['rate']}</div>
                    <div style="font-size: 10px; color: #8b949e;">Next: {info['next']}</div>
                    <div style="font-size: 10px; color: #FF9900;">{info['sentiment']}</div>
                </div>
            """, unsafe_allow_html=True)

