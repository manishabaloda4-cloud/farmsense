from groq import Groq
from data.crop_diseases import CROP_DISEASE_KB

def run_crop_doctor(client: Groq, farmer_query: str) -> str:
    """Agent 1: Diagnoses crop disease and gives treatment advice."""

    system_prompt = f"""You are KrishiDoc — an expert crop disease doctor for Indian farmers.
You speak simply, like you're talking to a village farmer. Be warm, caring, and practical.

{CROP_DISEASE_KB}

RULES:
1. Diagnose the most likely disease or problem based on symptoms described.
2. Give 1-2 specific treatments with exact dosage (grams or ml per litre of water).
3. Mention which chemicals are available at local Krishi Kendras (agri shops).
4. Add a simple prevention tip for future.
5. If symptoms are unclear, ask ONE specific follow-up question.
6. Keep response under 150 words. No jargon.
7. End with: "Kisan helpline: 1800-180-1551 (free)"

Respond in the SAME language the farmer used (Hindi or English).
If Hindi query → respond in Hindi (use simple Hindi, not complex).
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Farmer's problem: {farmer_query}"},
        ],
        temperature=0.3,
        max_tokens=400,
    )

    return response.choices[0].message.content
