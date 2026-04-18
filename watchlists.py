import streamlit as st
import textwrap
import json
import os

WATCHLIST_FILE = "watchlists.json"

def load_watchlists():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return {"Default": ["EURUSD=X", "GBPUSD=X", "GC=F", "NQ=F"]}

def save_watchlists(data):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f)

def render_watchlists():
    st.markdown(textwrap.dedent("""
        <h2 style='color: #FF9900; font-family: monospace; border-bottom: 1px solid #30363d; padding-bottom:10px;'>
            [CUSTOM WATCHLISTS: ELITE]
        </h2>
    """), unsafe_allow_html=True)
    
    watchlists = load_watchlists()
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### Manage Lists")
        new_list_name = st.text_input("New List Name")
        if st.button("Create List"):
            if new_list_name and new_list_name not in watchlists:
                watchlists[new_list_name] = []
                save_watchlists(watchlists)
                st.rerun()
        
        selected_list = st.selectbox("Select Active List", list(watchlists.keys()))
        
    with c2:
        st.markdown(f"### Assets in {selected_list}")
        new_asset = st.text_input("Add Asset (e.g. AAPL, BTC-USD)")
        if st.button("Add to List"):
            if new_asset and new_asset not in watchlists[selected_list]:
                watchlists[selected_list].append(new_asset)
                save_watchlists(watchlists)
                st.rerun()
        
        st.markdown("---")
        for asset in watchlists[selected_list]:
            bc1, bc2 = st.columns([4, 1])
            bc1.write(f"🔹 **{asset}**")
            if bc2.button("🗑", key=f"del_{asset}"):
                watchlists[selected_list].remove(asset)
                save_watchlists(watchlists)
                st.rerun()
