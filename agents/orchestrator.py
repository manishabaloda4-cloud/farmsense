import concurrent.futures
from groq import Groq
from agents.crop_doctor import run_crop_doctor
from agents.weather_scout import run_weather_scout
from agents.market_advisor import run_market_advisor

def detect_language(text: str) -> str:
    """Simple Hindi detection by checking for Devanagari characters."""
    for char in text:
        if '\u0900' <= char <= '\u097F':
            return "hi"
    hindi_words = ["mera", "mere", "meri", "ki", "ke", "ka", "hai", "hain",
                   "kya", "kaise", "nahi", "aur", "se", "ko", "me", "par"]
    words = text.lower().split()
    if sum(1 for w in words if w in hindi_words) >= 2:
        return "hi"
    return "en"

def detect_query_type(query: str) -> dict:
    """Detect what the farmer is asking about."""
    query_lower = query.lower()

    needs_disease = any(word in query_lower for word in [
        "disease", "pest", "yellow", "brown", "black", "wilt", "rot", "spots",
        "leaves", "dying", "blight", "fungus", "insect", "bug", "damage",
        "patte", "rog", "keeda", "peele", "sukh", "mar", "damage", "problem",
        "issue", "help", "kheti", "fasal"
    ])

    needs_market = any(word in query_lower for word in [
        "price", "sell", "market", "mandi", "rate", "bhav", "bikri",
        "becho", "dam", "paisa", "rupee", "profit", "income"
    ])

    if not needs_disease and not needs_market:
        needs_disease = True

    return {
        "disease": needs_disease,
        "weather": True,
        "market": needs_market or needs_disease,
    }

def run_orchestrator(groq_api_key: str, farmer_query: str, location: str) -> dict:
    """
    Main orchestrator: runs sub-agents in parallel and merges results.
    This is the multi-agent ADK pattern — orchestrator coordinates specialists.
    """
    client = Groq(api_key=groq_api_key)
    language = detect_language(farmer_query)
    query_types = detect_query_type(farmer_query)

    results = {
        "query": farmer_query,
        "location": location,
        "language": language,
        "crop_advice": None,
        "weather_advice": None,
        "market_advice": None,
    }

    tasks = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        if query_types["disease"]:
            tasks["crop"] = executor.submit(run_crop_doctor, client, farmer_query)
        if query_types["weather"]:
            tasks["weather"] = executor.submit(run_weather_scout, client, farmer_query, location, language)
        if query_types["market"]:
            tasks["market"] = executor.submit(run_market_advisor, client, farmer_query, location, language)

        for key, future in tasks.items():
            try:
                if key == "crop":
                    results["crop_advice"] = future.result(timeout=30)
                elif key == "weather":
                    results["weather_advice"] = future.result(timeout=30)
                elif key == "market":
                    results["market_advice"] = future.result(timeout=30)
            except Exception as e:
                results[f"{key}_error"] = str(e)

    return results
