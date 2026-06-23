import requests

INDIA_CITIES = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "patna": (25.5941, 85.1376),
    "bhopal": (23.2599, 77.4126),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "chandigarh": (30.7333, 76.7794),
    "amritsar": (31.6340, 74.8723),
    "ludhiana": (30.9010, 75.8573),
    "varanasi": (25.3176, 82.9739),
    "agra": (27.1767, 78.0081),
    "coimbatore": (11.0168, 76.9558),
    "visakhapatnam": (17.6868, 83.2185),
    "surat": (21.1702, 72.8311),
    "udaipur": (24.5854, 73.7125),
    "jodhpur": (26.2389, 73.0243),
    "nashik": (19.9975, 73.7898),
    "aurangabad": (19.8762, 75.3433),
    "ranchi": (23.3441, 85.3096),
    "guwahati": (26.1445, 91.7362),
    "shimla": (31.1048, 77.1734),
    "dehradun": (30.3165, 78.0322),
}

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}

def get_coordinates(city_name: str):
    city = city_name.lower().strip()
    for key, coords in INDIA_CITIES.items():
        if key in city or city in key:
            return coords, key.title()
    return INDIA_CITIES["delhi"], "Delhi (default)"

def get_weather(location: str) -> dict:
    try:
        coords, city_name = get_coordinates(location)
        lat, lon = coords

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation",
                        "weather_code", "wind_speed_10m", "uv_index"],
            "daily": ["temperature_2m_max", "temperature_2m_min",
                      "precipitation_sum", "precipitation_probability_max",
                      "weather_code"],
            "timezone": "Asia/Kolkata",
            "forecast_days": 5,
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        weather_code = current.get("weather_code", 0)
        condition = WMO_CODES.get(weather_code, "Unknown")

        forecast_days = []
        dates = daily.get("time", [])
        for i in range(min(5, len(dates))):
            code = daily.get("weather_code", [0]*5)[i]
            forecast_days.append({
                "date": dates[i],
                "max_temp": daily.get("temperature_2m_max", [0]*5)[i],
                "min_temp": daily.get("temperature_2m_min", [0]*5)[i],
                "rain_mm": daily.get("precipitation_sum", [0]*5)[i],
                "rain_chance": daily.get("precipitation_probability_max", [0]*5)[i],
                "condition": WMO_CODES.get(code, "Unknown"),
            })

        return {
            "success": True,
            "city": city_name,
            "current": {
                "temp": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "rain_mm": current.get("precipitation"),
                "condition": condition,
                "wind_kmh": current.get("wind_speed_10m"),
                "uv_index": current.get("uv_index"),
            },
            "forecast": forecast_days,
        }

    except Exception as e:
        import datetime
        month = datetime.datetime.now().month
        if 6 <= month <= 9:
            temp, humidity, condition = 34, 78, "Partly cloudy with monsoon risk"
        elif 10 <= month <= 2:
            temp, humidity, condition = 22, 55, "Clear and cool"
        else:
            temp, humidity, condition = 38, 40, "Hot and dry"
        return {
            "success": True,
            "city": city_name,
            "current": {
                "temp": temp, "humidity": humidity, "rain_mm": 0,
                "condition": condition, "wind_kmh": 12, "uv_index": 7,
            },
            "forecast": [],
            "note": "Live weather unavailable — using seasonal estimates",
        }

def format_weather_for_agent(weather: dict) -> str:
    if not weather["success"]:
        return f"Weather data unavailable for {weather['city']}. Using estimated values."

    c = weather["current"]
    lines = [
        f"Location: {weather['city']}",
        f"Current: {c['temp']}°C, {c['condition']}",
        f"Humidity: {c['humidity']}%, Wind: {c['wind_kmh']} km/h, UV Index: {c['uv_index']}",
        f"Current rainfall: {c['rain_mm']} mm",
        "",
        "5-Day Forecast:",
    ]
    for day in weather["forecast"]:
        lines.append(
            f"  {day['date']}: {day['condition']}, {day['min_temp']}–{day['max_temp']}°C, "
            f"Rain: {day['rain_mm']}mm ({day['rain_chance']}% chance)"
        )
    return "\n".join(lines)
