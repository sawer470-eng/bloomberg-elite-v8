import streamlit as st
import textwrap
import google.generativeai as genai

def render_ai_intelligence():
    st.markdown(textwrap.dedent("""
        <h2 style='color: #FF9900; font-family: monospace; border-bottom: 2px solid rgba(255, 153, 0, 0.4); padding-bottom:10px;'>
            [AI MARKET INTELLIGENCE: ELITE]
        </h2>
    """), unsafe_allow_html=True)
    
    # Exclusively use key from secrets for security (not visible to users)
    secrets_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if secrets_key:
        st.session_state.gemini_api_key = secrets_key
        st.sidebar.info("🤖 Gemini Engine: ACTIVE")
    else:
        st.sidebar.error("❌ Gemini Engine: DISCONNECTED")
        st.sidebar.markdown("<p style='font-size: 10px; color: #8b949e;'>Owner: Add GEMINI_API_KEY to st.secrets</p>", unsafe_allow_html=True)
    
    if not st.session_state.get("gemini_api_key"):
        st.info("💡 Connect your Gemini API key in the sidebar to unlock professional analysis.")
        st.markdown("#### Institutional Macro Reasoning (Pre-Canned)")
        
        scenarios = {
            "Hawkish Shift": "Central Bank signals higher rates for longer. Outcome: Stronger Currency, Lower Equities.",
            "Inflation Beat": "CPI data higher than expected. Outcome: Yields Rise, Gold pressured, USD Strengthens.",
            "Dovish Pivot": "Signs of cooling labor market. Outcome: Rates likely to fall, Equities Bullish, Gold Bullish."
        }
        
        for title, desc in scenarios.items():
            with st.expander(f"🧠 Analysis: {title}"):
                st.write(desc)
    else:
        st.markdown("#### Active AI Capabilities")
        st.write("1. **News Summarization**: Active in the Live News Feed.")
        st.write("2. **Macro Synthesis**: Automatically analyzes cross-asset moves.")
        
        if 'last_ai_summary' in st.session_state:
            st.markdown("---")
            st.markdown("### Latest AI Analysis Result")
            st.info(st.session_state.last_ai_summary)

def get_gemini_summary(text, headline=""):
    if 'gemini_api_key' not in st.session_state or not st.session_state.gemini_api_key:
        return "Please provide a Gemini API key in the sidebar."
    
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a professional Bloomberg Terminal analyst. 
        Summarize the following financial news headline and content. 
        Focus on:
        1. Market Impact (Bullish/Bearish for which assets).
        2. Institutional Reasoning.
        3. Key levels to watch.
        
        Headline: {headline}
        Content: {text}
        
        Keep it concise and technical.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"
