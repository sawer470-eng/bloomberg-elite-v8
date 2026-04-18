import streamlit as st
import feedparser
import textwrap
from ai_intelligence import get_gemini_summary

def render_news_feed():
    st.markdown(textwrap.dedent("""
        <h2 style='color: #FF9900; font-family: monospace; border-bottom: 1px solid #30363d; padding-bottom:10px;'>
            [LIVE NEWS FEED & INTELLIGENCE]
        </h2>
    """), unsafe_allow_html=True)
    
    # Example RSS feeds
    rss_urls = [
        ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
        ("Wall Street Journal", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
    ]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_feed = st.radio("Select Source", [n for n, u in rss_urls], horizontal=True)
    
    feed_url = next(u for n, u in rss_urls if n == selected_feed)
    
    with st.spinner("Fetching Live Market Intelligence..."):
        try:
            feed = feedparser.parse(feed_url)
        except:
            st.error("Network error: Could not reach news server.")
            return
            
    if not feed.entries:
        st.error("Could not load news feed entries.")
        return
        
    st.markdown("---")
    
    for i, entry in enumerate(feed.entries[:15]):
        published = entry.get('published', 'No Date')
        title = entry.get('title', 'No Title')
        summary = entry.get('summary', '')
        link = entry.get('link', '#')
        
        with st.expander(f"📰 {title}"):
            st.markdown(textwrap.dedent(f"""
                <div style="font-family: 'Inter', sans-serif;">
                    <div style="color: #45a29e; font-size: 11px; margin-bottom: 5px;">Published: {published}</div>
                    <p style="color: #c5c6c7; font-size: 14px;">{summary[:300]}...</p>
                    <a href="{link}" target="_blank" style="color: #FF9900; font-size: 13px; text-decoration: none;">[Read Full Article]</a>
                </div>
            """), unsafe_allow_html=True)
            
            st.write("") # Spacer
            # AI & Edge Buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(f"🔍 ANALYZE 5Y IMPACT", key=f"edge_{i}_{link[:20]}"):
                    st.session_state.selected_news_event = title
                    st.session_state.current_page = "12. News Impact Lab (ELITE)"
                    st.rerun()
            with col_b:
                if st.button(f"💎 GEMINI AI SUMMARY", key=f"ai_{i}_{link[:20]}"):
                    with st.spinner("AI is analyzing headline..."):
                        summary = get_gemini_summary(summary, title)
                        st.session_state.last_ai_summary = summary
                        st.session_state.current_page = "11. AI Intelligence Lab (PRO)"
                        st.rerun()
