# 🌾 FarmSense — AI Agent for Indian Farmers
### Kaggle AI Agents Capstone 2026 | Agents for Good Track

FarmSense is a multi-agent AI system that helps Indian farmers diagnose crop diseases, get weather-based spraying advice, and make smart selling decisions — in Hindi or English.

---

## 🤖 Agent Architecture

```
Farmer Query (Hindi/English)
         ↓
   Orchestrator Agent  ←── detects language, routes to agents in parallel
    /       |       \
   ↓        ↓        ↓
Crop     Weather   Market
Doctor   Scout     Advisor
   ↓        ↓        ↓
Groq    Open-Meteo  data.gov.in
Llama3  API (MCP)   Agmarknet API
   \        |        /
    ↓       ↓       ↓
     Merged Response
         ↓
   Streamlit Web UI
```

## ✅ Course Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Multi-agent system | Orchestrator + 3 specialist sub-agents |
| Agent tools (MCP) | Open-Meteo weather API, data.gov.in price API |
| Agent skills | Crop disease knowledge base skill |
| Parallel execution | ThreadPoolExecutor for simultaneous agents |
| Security | API keys in .env, never hardcoded |
| Bilingual support | Auto-detects Hindi/English, responds in same language |

---

## 🚀 Setup & Run

### 1. Clone and install
```bash
git clone <your-repo>
cd farmsense
pip install -r requirements.txt
```

### 2. Set your API key
```bash
cp .env.example .env
# Edit .env and add your Groq API key
# Get free key at: console.groq.com
```

### 3. Run the app
```bash
cd ui
streamlit run app.py
```

---

## 📁 Project Structure

```
farmsense/
├── agents/
│   ├── orchestrator.py      # Main coordinator agent
│   ├── crop_doctor.py       # Disease diagnosis agent
│   ├── weather_scout.py     # Weather advisory agent
│   └── market_advisor.py    # Market price agent
├── tools/
│   ├── weather_tool.py      # Open-Meteo API integration
│   └── market_tool.py       # Agmarknet + MSP data
├── data/
│   └── crop_diseases.py     # Crop disease knowledge base
├── ui/
│   └── app.py               # Streamlit web interface
├── requirements.txt
└── README.md
```

---

## 🌍 Impact

- Serves 600M+ Indian farmers who can't afford agronomists
- Works in Hindi and English
- Uses free APIs — zero cost for farmers
- Covers 5 major crops: tomato, wheat, rice, cotton, maize

---

## 🔗 Resources
- **eNAM mandi portal:** enam.gov.in
- **PM-KISAN:** pmkisan.gov.in
- **Kisan helpline:** 1800-180-1551 (free, 24x7)
- **Groq API (free):** console.groq.com
