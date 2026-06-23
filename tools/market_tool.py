import requests

MSP_2024_25 = {
    "wheat": {"msp": 2275, "unit": "quintal"},
    "rice": {"msp": 2300, "unit": "quintal"},
    "paddy": {"msp": 2300, "unit": "quintal"},
    "maize": {"msp": 2090, "unit": "quintal"},
    "soybean": {"msp": 4892, "unit": "quintal"},
    "cotton": {"msp": 7121, "unit": "quintal"},
    "groundnut": {"msp": 6783, "unit": "quintal"},
    "sunflower": {"msp": 7280, "unit": "quintal"},
    "sugarcane": {"msp": 340, "unit": "quintal"},
    "gram": {"msp": 5440, "unit": "quintal"},
    "chana": {"msp": 5440, "unit": "quintal"},
    "arhar": {"msp": 7550, "unit": "quintal"},
    "tur": {"msp": 7550, "unit": "quintal"},
    "moong": {"msp": 8682, "unit": "quintal"},
    "urad": {"msp": 7400, "unit": "quintal"},
    "mustard": {"msp": 5950, "unit": "quintal"},
    "rapeseed": {"msp": 5950, "unit": "quintal"},
    "bajra": {"msp": 2625, "unit": "quintal"},
    "jowar": {"msp": 3371, "unit": "quintal"},
    "ragi": {"msp": 4290, "unit": "quintal"},
    "tomato": {"msp": None, "unit": "quintal"},
    "onion": {"msp": None, "unit": "quintal"},
    "potato": {"msp": None, "unit": "quintal"},
}

SEASONAL_ADVICE = {
    "kharif": ["rice", "paddy", "maize", "cotton", "soybean", "groundnut",
               "bajra", "jowar", "arhar", "tur", "moong", "urad", "sugarcane"],
    "rabi": ["wheat", "gram", "chana", "mustard", "rapeseed", "sunflower", "ragi"],
    "zaid": ["tomato", "onion", "potato", "maize"],
}

def detect_crop(query: str) -> str:
    query_lower = query.lower()
    for crop in MSP_2024_25:
        if crop in query_lower:
            return crop
    return None

def get_current_season() -> str:
    import datetime
    month = datetime.datetime.now().month
    if 6 <= month <= 10:
        return "kharif"
    elif 11 <= month <= 3:
        return "rabi"
    else:
        return "zaid"

def get_market_info(crop_name: str, location: str = "India") -> dict:
    crop = crop_name.lower().strip()

    msp_info = MSP_2024_25.get(crop, {})
    current_season = get_current_season()

    in_season = any(crop in crops for season, crops in SEASONAL_ADVICE.items()
                    if season == current_season)

    try:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": "579b464db66ec23bdd000001cdd3946e44ce4aae38d976952d56929",
            "format": "json",
            "filters[commodity]": crop_name.title(),
            "limit": 5,
        }
        resp = requests.get(url, params=params, timeout=8)
        market_data = resp.json()
        records = market_data.get("records", [])
    except Exception:
        records = []

    return {
        "crop": crop,
        "msp": msp_info.get("msp"),
        "unit": msp_info.get("unit", "quintal"),
        "current_season": current_season,
        "in_season": in_season,
        "market_records": records[:3],
        "location": location,
    }

def format_market_for_agent(info: dict) -> str:
    lines = [f"Crop: {info['crop'].title()}"]

    if info["msp"]:
        lines.append(f"Government MSP (2024-25): ₹{info['msp']} per {info['unit']}")
    else:
        lines.append("No fixed MSP for this crop (market-driven price)")

    lines.append(f"Current season: {info['current_season'].title()}")
    lines.append(f"In-season crop: {'Yes' if info['in_season'] else 'No'}")

    if info["market_records"]:
        lines.append("\nRecent mandi prices:")
        for r in info["market_records"]:
            lines.append(
                f"  {r.get('market', 'N/A')}, {r.get('state', '')}: "
                f"₹{r.get('modal_price', 'N/A')}/quintal"
            )
    else:
        lines.append("\nLive mandi data unavailable. Check: enam.gov.in or agmarknet.gov.in")

    return "\n".join(lines)
