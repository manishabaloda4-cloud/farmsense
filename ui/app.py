import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import run_orchestrator
from tools.weather_tool import get_weather, INDIA_CITIES

st.set_page_config(
    page_title="FarmSense — AI for Indian Farmers",
    page_icon="🌾",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 2.4rem; font-weight: 700; color: #1a5c38;
    text-align: center; margin-bottom: 0.2rem; letter-spacing: -0.5px;
}
.subtitle {
    text-align: center; color: #52796f; font-size: 1rem; margin-bottom: 2rem;
}
.agent-card {
    background: #f0faf4; border-left: 5px solid #2d6a4f;
    padding: 1.2rem 1.4rem; border-radius: 10px; margin-bottom: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.agent-card.weather { border-left-color: #1565c0; background: #e8f4fd; }
.agent-card.market  { border-left-color: #c62828; background: #fff3e0; }
.agent-label {
    font-weight: 700; font-size: 0.78rem; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 0.6rem; display: flex; align-items: center; gap: 6px;
}
.agent-label.green  { color: #1a5c38; }
.agent-label.blue   { color: #1565c0; }
.agent-label.orange { color: #c62828; }
.agent-body { font-size: 0.97rem; line-height: 1.75; color: #1a1a1a; }
.badge {
    display: inline-block; background: #e8f5e9; color: #2d6a4f;
    font-size: 0.72rem; font-weight: 600; padding: 2px 10px;
    border-radius: 20px; margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌾 FarmSense</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI assistant for Indian farmers · किसानों का डिजिटल सहायक</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center"><span class="badge">🏆 Kaggle AI Agents Capstone 2026 · Agents for Good</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

    st.markdown("### 📍 Your Location")
    city_list = sorted([c.title() for c in INDIA_CITIES.keys()])
    selected_city = st.selectbox("Select your district/city", city_list, index=city_list.index("Udaipur"))

    st.markdown("---")
    st.markdown("### 🌤️ Current Weather")
    weather = get_weather(selected_city)
    if weather["success"]:
        c = weather["current"]
        col1, col2 = st.columns(2)
        col1.metric("Temperature", f"{c['temp']}°C")
        col2.metric("Humidity", f"{c['humidity']}%")
        col1.metric("Condition", c["condition"][:12])
        col2.metric("Rain", f"{c['rain_mm']} mm")

    st.markdown("---")
    st.markdown("**📞 Kisan Helpline:** 1800-180-1551")
    st.markdown("**💰 PM-KISAN:** pmkisan.gov.in")
    st.markdown("**🏪 eNAM Mandi:** enam.gov.in")
    st.markdown("---")
    st.markdown("""
    <small style='color:#888'>
    <b>How it works:</b><br>
    3 AI agents run in parallel:<br>
    🩺 Crop Doctor<br>
    🌤️ Weather Scout<br>
    📊 Market Advisor
    </small>
    """, unsafe_allow_html=True)

st.markdown("### 📝 Describe your crop problem")
st.markdown("*Type in Hindi or English — हिंदी या अंग्रेजी में लिखें*")

examples = [
    "My tomato leaves are turning yellow and falling off",
    "Wheat crop has orange powder on leaves",
    "Mere dhaan ke patte par bhoore dabbe aa rahe hain",
    "Cotton plant is wilting from bottom, what to do?",
    "What is the price of wheat today, should I sell?",
    "Meri fasal mein keede lag gaye hain, kya karoon?",
]

st.markdown("**Quick examples:**")
cols = st.columns(2)
for i, ex in enumerate(examples):
    with cols[i % 2]:
        if st.button(f"📌 {ex[:38]}...", key=f"ex_{i}", use_container_width=True):
            st.session_state["farmer_query"] = ex

query_val = st.session_state.get("farmer_query", "")
farmer_query = st.text_area(
    "Your question",
    value=query_val,
    height=110,
    placeholder="e.g. My rice crop has brown spots on leaves and the plants are wilting...",
    label_visibility="collapsed",
)

ask_btn = st.button("🔍 Get Expert Advice", type="primary", use_container_width=True)

if ask_btn:
    if not groq_api_key:
        st.error("⚠️ Please enter your Groq API key in the sidebar.")
        st.stop()
    if not farmer_query.strip():
        st.warning("⚠️ Please describe your crop problem first.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🤖 FarmSense Agent Analysis")

    with st.spinner("🌾 Three AI agents are analyzing your problem in parallel..."):
        try:
            results = run_orchestrator(groq_api_key, farmer_query, selected_city)
        except Exception as e:
            import traceback
            st.error(f"❌ Error: {e}")
            st.stop()

    crop     = results.get("crop_advice")
    weather_a = results.get("weather_advice")
    market   = results.get("market_advice")

    if not crop and not weather_a and not market:
        st.error("⚠️ All agents returned empty. Check your API key and try again.")
        st.stop()

    st.success("✅ Analysis complete! Here are your results:")

    if crop:
        st.markdown(f"""
<div class="agent-card">
  <div class="agent-label green">🩺 Crop Doctor — Disease &amp; Treatment Advice</div>
  <div class="agent-body">{crop.replace(chr(10), '<br>')}</div>
</div>""", unsafe_allow_html=True)

    if weather_a:
        st.markdown(f"""
<div class="agent-card weather">
  <div class="agent-label blue">🌤️ Weather Scout — Spraying &amp; Farming Advice</div>
  <div class="agent-body">{weather_a.replace(chr(10), '<br>')}</div>
</div>""", unsafe_allow_html=True)

    if market:
        st.markdown(f"""
<div class="agent-card market">
  <div class="agent-label orange">📊 Market Advisor — Price &amp; Selling Advice</div>
  <div class="agent-body">{market.replace(chr(10), '<br>')}</div>
</div>""", unsafe_allow_html=True)

    lang = results.get("language", "en")
    if lang == "hi":
        st.info("💬 Hindi query detected — all responses given in Hindi")

    st.markdown("---")
    st.markdown("""
    <div style='background:#f8f9fa;border-radius:10px;padding:1rem 1.2rem;font-size:0.85rem;color:#555'>
    <b>🔧 Agent Architecture Used</b><br><br>
    <b>Orchestrator Agent</b> → detected language, routed to 3 specialist agents in parallel<br>
    <b>🩺 Crop Doctor</b> → Groq Llama-3.3-70b + crop disease knowledge base skill<br>
    <b>🌤️ Weather Scout</b> → Open-Meteo weather API tool (MCP pattern)<br>
    <b>📊 Market Advisor</b> → data.gov.in Agmarknet API + MSP 2024-25 database<br>
    <b>⚡ Parallel Execution</b> → all 3 agents run simultaneously via ThreadPoolExecutor<br>
    <b>🔒 Security</b> → API keys in .env, never hardcoded
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:0.78rem;padding-bottom:1rem'>"
    "FarmSense · Built for Kaggle AI Agents Capstone 2026 · Agents for Good Track · "
    "Powered by Groq Llama-3.3-70b"
    "</div>",
    unsafe_allow_html=True
)
