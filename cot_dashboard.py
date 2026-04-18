import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import textwrap
from data_fetcher import COTFetcher
from analyzer import COTAnalyzer

def render_cot_dashboard():
    st.markdown("<h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>[SMC & COT POSITIONING ANALYSIS]</h2>", unsafe_allow_html=True)
    
    # Essential local styles for COT specific elements
    st.markdown("""
<style>
.delta-positive { color: #66ff00; font-size: 14px; font-family: 'JetBrains Mono'; }
.delta-negative { color: #ff0033; font-size: 14px; font-family: 'JetBrains Mono'; }
.percentile-bar {
    width: 100%;
    height: 12px;
    background: rgba(69, 162, 158, 0.05);
    border-radius: 6px;
    position: relative;
    margin-top: 10px;
    margin-bottom: 5px;
    border: 1px solid rgba(69, 162, 158, 0.2);
    overflow: visible;
}
.percentile-marker {
    width: 16px;
    height: 16px;
    background-color: #FF9900;
    border-radius: 50%;
    position: absolute;
    top: -3px;
    border: 3px solid #000;
    box-shadow: 0 0 10px rgba(255, 153, 0, 0.5);
    transition: left 0.5s ease;
}
</style>
""", unsafe_allow_html=True)
    
    # Временно отключаем кэш, чтобы заставить систему стянуть свежие данные с нуля
    # @st.cache_data(ttl=3600)
    def load_tff_data_fresh():
        fetcher = COTFetcher()
        df = fetcher.fetch_recent_data('traders_in_financial_futures_fut')
        return df
    
    with st.spinner("Fetching Fresh TFF Data (Live)..."):
        raw_data = load_tff_data_fresh()
    
    if raw_data is not None and not raw_data.empty:
        analyzer = COTAnalyzer(raw_data)
        assets = analyzer.get_assets()
        
        # DEBUG OUTPUT FOR USER
        if not len(assets):
            st.warning("Внимание: список активов пуст. Отладочная информация колонок:")
            st.write(raw_data.columns.tolist()[:30])
            
        common_names = [a for a in assets if 'EURO' in str(a) or 'GOLD' in str(a) or 'BRITISH' in str(a) or 'YEN' in str(a) or 'AUSTRALIAN' in str(a)]
        all_options = common_names + [a for a in assets if a not in common_names]
    
        # Top Selector
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_asset = st.selectbox("SELECT CONTRACT", options=all_options)
        
        if selected_asset:
            asset_df = analyzer.analyze_asset(selected_asset)
            
            if asset_df is not None and not asset_df.empty:
                latest = asset_df.iloc[-1]
                
                # Formatting helpers
                def format_val(val): return f"+{val:,.0f}" if val > 0 else f"{val:,.0f}"
                def delta_html(val): 
                    if pd.isna(val): return ""
                    return f"<div class='delta-positive'>+{val:,.0f} за нед.</div>" if val > 0 else f"<div class='delta-negative'>{val:,.0f} за нед.</div>"
    
                # --- TOP METRICS ROW ---
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
<div class="metric-title">ASSET MANAGERS (NET)</div>
<div class="metric-value">{format_val(latest.get('Net Asset Mgr',0))}</div>
{delta_html(latest.get('Delta Asset Mgr', 0))}
</div>
"""), unsafe_allow_html=True)
                    
                with c2:
                    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
<div class="metric-title">LEVERAGED FUNDS (NET)</div>
<div class="metric-value">{format_val(latest.get('Net Lev Money',0))}</div>
{delta_html(latest.get('Delta Lev Money', 0))}
</div>
"""), unsafe_allow_html=True)
                    
                with c3:
                    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
<div class="metric-title">DEALERS (NET)</div>
<div class="metric-value">{format_val(latest.get('Net Dealer',0))}</div>
{delta_html(latest.get('Delta Dealer', 0))}
</div>
"""), unsafe_allow_html=True)
                    
                with c4:
                    oi_delta = latest.get('Delta Open Interest', 0)
                    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
<div class="metric-title">OPEN INTEREST</div>
<div class="metric-value">{latest.get('Open_Interest_All',0):,.0f}</div>
{delta_html(oi_delta)}
</div>
"""), unsafe_allow_html=True)
    
                # --- ANALYSIS ROW ---
                am_dir, am_dyn, lev_mood, lev_dyn, percentile = analyzer.get_smart_money_bias(asset_df)
                
                # Predict probability based on percentile
                prob_long = percentile 
                prob_text = f"Upside Probability: {prob_long:.1f}%"
                
                st.markdown(f"### Position Lifecycle Analysis")
                c_left, c_right = st.columns(2)
                
                with c_left:
                    html_left = f"""<div class="metric-card" style="height: 250px;">
    <div class="metric-title">SMART MONEY BIAS (ASSET MANAGERS)</div>
    <div style="color:{'#3fb950' if 'ЛОНГ' in am_dir else '#f85149'}; font-size: 18px; font-weight:bold; margin-bottom: 20px;">
    {am_dir.replace('ЛОНГ', 'BULLISH').replace('ШОРТ', 'BEARISH')}
    </div>
    <div class="metric-title" style="margin-top: 20px;">LEVERAGED FUNDS — SENTIMENT</div>
    <div style="color:{'#3fb950' if 'ЛОНГ' in lev_mood else '#f85149'}; font-size: 18px; font-weight:bold;">
    {lev_mood.replace('ЛОНГ', 'BULLISH').replace('ШОРТ', 'BEARISH')}
    </div>
    <div style="color:#8b949e; font-size: 14px; margin-top: 5px;">{lev_dyn.replace('Наращивают позиции', 'Accumulating').replace('Сокращают позиции', 'Liquidating')}</div>
    </div>"""
                    st.markdown(html_left, unsafe_allow_html=True)
                    
                with c_right:
                    perc_color = "#3fb950" if 15 <= percentile <= 85 else "#f85149"
                    perc_status = "в пределах нормы" if 15 <= percentile <= 85 else "экстремальная зона"
                    html_right = f"""<div class="metric-card" style="height: 250px;">
    <div class="metric-title">WEEKLY FLOW (SMART MONEY)</div>
    <div style="color:{'#3fb950' if 'Наращивают' in am_dyn else '#f85149'}; font-size: 16px; margin-bottom: 30px;">
    {am_dyn.replace('Наращивают позиции', 'Increasing Exposure').replace('Сокращают позиции', 'Decreasing Exposure')}
    </div>
    <div class="metric-title">POSITION PERCENTILE (1 YEAR)</div>
    <div style="color:{perc_color}; font-size: 16px; margin-bottom: 10px;">
    {percentile:.0f}% — {'In Range' if 15 <= percentile <= 85 else 'Extreme Zone'}
    </div>
    <div class="percentile-bar">
    <div class="percentile-marker" style="left: {percentile}%;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size: 12px; color:#8b949e; margin-top:5px;">
    <span>0%<br>Extr. Short</span>
    <span>15%</span>
    <span style="color:#3fb950;">Neutral Zone</span>
    <span>85%</span>
    <span>100%<br>Extr. Long</span>
    </div>
    <div style="color:#c9d1d9; font-size: 14px; margin-top: 15px; text-align: center;">
    <b>{prob_text}</b>
    </div>
    </div>"""
                    st.markdown(html_right, unsafe_allow_html=True)
    
                # --- MULTILINE CHART ---
                st.markdown(f"### Net Positioning Flow — TFF Report")
                fig = go.Figure()
    
                # Colors matching the image
                fig.add_trace(go.Scatter(x=asset_df['Date'], y=asset_df['Net Asset Mgr'], mode='lines', name='Asset Managers', line=dict(color='#3fb950', width=2)))
                fig.add_trace(go.Scatter(x=asset_df['Date'], y=asset_df['Net Lev Money'], mode='lines', name='Leveraged Funds', line=dict(color='#8957e5', width=2)))
                fig.add_trace(go.Scatter(x=asset_df['Date'], y=asset_df['Net Dealer'], mode='lines', name='Dealers', line=dict(color='#f85149', width=2)))
                fig.add_trace(go.Scatter(x=asset_df['Date'], y=asset_df['Net Other'], mode='lines', name='Other', line=dict(color='#d29922', width=2, dash='dot')))
                
                fig.update_layout(
                    height=500,
                    plot_bgcolor='#161b22',
                    paper_bgcolor='#0d1117',
                    font=dict(color='#8b949e'),
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#30363d')
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
            else:
                st.warning("Нет данных для данного контракта.")
    else:
                st.error("Ошибка загрузки данных.")
    
