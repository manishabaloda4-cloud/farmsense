from groq import Groq
from tools.market_tool import get_market_info, format_market_for_agent, detect_crop

def run_market_advisor(client: Groq, farmer_query: str, location: str, language: str = "en") -> str:
    """Agent 3: Gives crop price and selling advice."""

    crop = detect_crop(farmer_query)
    if not crop:
        words = farmer_query.lower().split()
        crop = words[0] if words else "crop"

    market_info = get_market_info(crop, location)
    market_data = format_market_for_agent(market_info)

    system_prompt = """You are MandiBuddy — a market advisor for Indian farmers.
Help the farmer make smart selling decisions.

RULES:
1. Tell the farmer the MSP (government minimum price) — they should never sell below this.
2. Advise whether to sell now or wait based on season.
3. Mention eNAM (enam.gov.in) for online mandi selling — better prices, no middlemen.
4. Mention PM-KISAN benefit reminder if relevant.
5. Keep it SHORT — 3-4 sentences max.
6. Be practical. Farmers need actionable advice, not theory.
7. Always give a price reference so they know if local traders are cheating them.

Respond in the same language as the farmer query (Hindi or English)."""

    user_msg = f"""Farmer's query: {farmer_query}
Location: {location}

Market data:
{market_data}

Give selling advice."""

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
