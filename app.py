import streamlit as st
import yfinance as yf
import textwrap
from data_engine import get_ticker_tape_data
from cot_dashboard import render_cot_dashboard
from market_data import render_market_data
from macro_data import render_macro_data
from news_feed import render_news_feed
from options_data import render_options_data
from correlation_data import render_correlation_matrix
from insider_data import render_insider_data
from tpo_data import render_tpo_data
from fair_value import render_fair_value_data
from news_impact import render_news_impact_data
from smc_scanner import render_smc_scanner
from ai_intelligence import render_ai_intelligence
from watchlists import render_watchlists
from liquidity_data import render_liquidity_data

st.set_page_config(page_title="Bloomberg Elite V3", layout="wide", page_icon="🏦")

# Global CSS for Premium Glassmorphism
css_style = textwrap.dedent("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Outfit:wght@500;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(18, 18, 24) 0%, rgb(0, 0, 0) 90.2%);
        font-family: 'Inter', sans-serif;
        color: #c5c6c7;
    }
    
    /* Metrics and Cards as Premium Glassmorphism */
    .metric-card {
        background: rgba(25, 27, 34, 0.45);
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border: 1px solid rgba(69, 162, 158, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover {
        transform: translateY(-8px);
        border-color: rgba(69, 162, 158, 0.6);
        background: rgba(30, 32, 40, 0.6);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.8), 0 0 20px rgba(69, 162, 158, 0.2);
    }
    
    .metric-title {
        color: #45a29e;
        font-family: 'Outfit', sans-serif;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
        opacity: 0.9;
    }
    .metric-value {
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 800;
        text-shadow: 0 0 15px rgba(69, 162, 158, 0.4);
    }
    
    /* TICKER TAPE CSS */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background: rgba(11, 12, 16, 0.9);
        backdrop-filter: blur(15px);
        box-sizing: content-box;
        border-bottom: 2px solid rgba(255, 153, 0, 0.6);
        white-space: nowrap;
        padding: 12px 0;
        margin-bottom: 30px;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .ticker {
        display: inline-block;
        padding-left: 100%;
        animation: ticker 50s linear infinite;
        font-weight: 600;
        font-size: 14px;
        font-family: 'JetBrains Mono', monospace;
    }
    @keyframes ticker {
        0%   { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(11, 12, 16, 0.98) !important;
        border-right: 1px solid rgba(69, 162, 158, 0.15);
    }
    
    /* Tabs and Headers */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 0%, #45a29e 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -0.5px;
    }
    
    /* Buttons and UI */
    .stButton>button {
        background: rgba(69, 162, 158, 0.15) !important;
        border: 1px solid rgba(69, 162, 158, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background: rgba(69, 162, 158, 0.3) !important;
        border-color: #45a29e !important;
    }
</style>
""")

st.markdown(css_style, unsafe_allow_html=True)

# Inject Ticker Tape with Redundant Data
ticker_content = get_ticker_tape_data()
tape_html = textwrap.dedent(f"""
<div class="ticker-wrap">
    <div class="ticker">
        {ticker_content} &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; {ticker_content} &nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp; {ticker_content}
    </div>
</div>
""")
st.markdown(tape_html, unsafe_allow_html=True)


st.sidebar.title("BLOOMBERG ELITE V3")
st.sidebar.markdown("---")

# Page Routing
menu = [
    "1. SMC & COT Analysis",
    "2. Market Heatmap & Treemap",
    "3. Macro Data & Calendar",
    "4. Correlation Matrix (ELITE)",
    "5. Options Sentiment (PRO)",
    "6. Insider Tracker (ELITE)",
    "7. Volume Profile TPO (ELITE)",
    "8. Fair Value & DCF (ELITE)",
    "9. SMC Scanner (ELITE NEW)",
    "10. Liquidity & Footprint (ELITE NEW)",
    "11. AI Intelligence Lab (PRO)",
    "12. News Impact Lab (ELITE)",
    "13. Live News Feed",
    "14. Custom Watchlists (PRO)"
]

# State Management for Navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = menu[0]

choice = st.sidebar.radio("NAVIGATION", menu, index=menu.index(st.session_state.current_page))
st.session_state.current_page = choice # Update state

if choice == "1. SMC & COT Analysis":
    render_cot_dashboard()
elif choice == "2. Market Heatmap & Treemap":
    render_market_data()
elif choice == "3. Macro Data & Calendar":
    render_macro_data()
elif choice == "4. Correlation Matrix (ELITE)":
    render_correlation_matrix()
elif choice == "5. Options Sentiment (PRO)":
    render_options_data()
elif choice == "6. Insider Tracker (ELITE)":
    render_insider_data()
elif choice == "7. Volume Profile TPO (ELITE)":
    render_tpo_data()
elif choice == "8. Fair Value & DCF (ELITE)":
    render_fair_value_data()
elif choice == "9. SMC Scanner (ELITE NEW)":
    render_smc_scanner()
elif choice == "10. Liquidity & Footprint (ELITE NEW)":
    render_liquidity_data()
elif choice == "11. AI Intelligence Lab (PRO)":
    render_ai_intelligence()
elif choice == "12. News Impact Lab (ELITE)":
    render_news_impact_data()
elif choice == "13. Live News Feed":
    render_news_feed()
elif choice == "14. Custom Watchlists (PRO)":
    render_watchlists()
