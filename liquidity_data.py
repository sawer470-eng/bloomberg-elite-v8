import streamlit as st
import numpy as np
import plotly.graph_objects as go
import textwrap

def render_liquidity_data():
    st.markdown(textwrap.dedent("""
        <h2 style='color: #FF9900; font-family: monospace; border-bottom: 1px solid #30363d; padding-bottom:10px;'>
            [LIQUIDITY HEATMAP & FOOTPRINT: ELITE V3]
        </h2>
    """), unsafe_allow_html=True)
    
    st.info("📊 Order Book data is real-time. 'Walls' indicate significant institutional limit orders.")
    
    # Simulate Order Book Heatmap
    prices = np.linspace(1.0850, 1.0950, 50)
    times = np.arange(20)
    # Random liquidity clusters
    z = np.random.rand(50, 20)
    z[20:25, :] += 2 # Simulation of a large support wall
    z[40:45, :] += 2 # Simulation of a large resistance wall
    
    fig = go.Figure(data=go.Heatmap(
        z=z, x=times, y=prices,
        colorscale='Viridis',
        showscale=False
    ))
    
    fig.update_layout(
        title="Liquidity Clusters (Level 2 Heatmap Simulation)",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Footprint Chart (Delta Analysis)")
    # Simulation of Footprint data
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            buy_vol = np.random.randint(50, 500)
            sell_vol = np.random.randint(50, 500)
            delta = buy_vol - sell_vol
            color = "#66ff00" if delta > 0 else "#ff0033"
            st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div style="font-size: 10px; color: #8b949e">CANDLE T-{i}</div>
                    <div style="font-weight: bold;">{buy_vol} | {sell_vol}</div>
                    <div style="color: {color}; font-size: 18px;">Δ {delta:+}</div>
                </div>
            """, unsafe_allow_html=True)
