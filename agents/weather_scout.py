from groq import Groq
from tools.weather_tool import get_weather, format_weather_for_agent

def run_weather_scout(client: Groq, farmer_query: str, location: str, language: str = "en") -> str:
    """Agent 2: Fetches weather and gives farming-specific advice."""

    weather = get_weather(location)
    weather_data = format_weather_for_agent(weather)

    system_prompt = """You are MausamMitra — a weather advisor for Indian farmers.
Your job: look at the weather data and tell the farmer what it means for their specific crop problem.

RULES:
1. Tell if today/this week is good or bad for spraying pesticides/fertilizers.
2. Warn if rain is expected (don't spray before rain — it washes away chemicals).
3. Advise best time of day to spray (morning 6-9am or evening 5-7pm, never afternoon).
4. If temperature is very high (>38°C) → warn about heat stress on crops.
5. If humidity is high (>80%) → warn about fungal disease risk.
6. Keep it SHORT — 3-4 sentences max.
7. Be farmer-friendly. No technical jargon.

Respond in the same language as the farmer query (Hindi or English)."""

    user_msg = f"""Farmer's problem: {farmer_query}
Location: {location}

Weather data:
{weather_data}

Give farming advice based on this weather."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
        max_tokens=300,
    )

    return response.choices[0].message.content
