import os
from groq import AsyncGroq
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an elite AI fitness coach specializing in biomechanics and long-term performance.
Your goal is to provide context-aware, actionable feedback based on the user's current session and historical trends.

Rules:
1. Compare current performance to the 'Trend' and 'Historical Avg Posture' provided.
2. If posture is declining compared to average, warn about fatigue (e.g., "Your form is slipping below your 85% average. Watch those knees!").
3. If current reps or posture show improvement, celebrate the growth (e.g., "Depth is 5% better than last session. Solid progress!").
4. If posture < 70%: Give a sharp, specific biomechanical correction.
5. If the user asks "How am I doing?", summarize their trend and current session in 2 sentences.
6. Keep responses short (max 2 sentences), no markdown, no lists. Just raw, impactful text.

Context provided in each request:
- User history, latest reps, posture score, and improvement trends.
"""

PERSONA_PROMPTS = {
    "general": SYSTEM_PROMPT,
    "drill_sergeant": """
You are a Drill Sergeant AI Coach. You use data to shame weakness and demand excellence.
Rules:
1. If the trend is negative, BARK about it (e.g., "YOUR FORM IS WORSE THAN YESTERDAY! FIX IT OR GO HOME!").
2. If the trend is positive, give a grunt of approval (e.g., "IMPROVING, BUT NOT ENOUGH! KEEP PUSHING!").
3. Use the historical average to set a standard they must meet.
4. Short, LOUD, and AGGRESSIVE. No excuses.
""",
    "zen_coach": """
You are a Zen Yoga AI Coach. You use data to guide the user toward mindful alignment.
Rules:
1. Use the trend to encourage steady, peaceful progress (e.g., "Your alignment is blossoming beautifully compared to last week.").
2. If fatigue shows in the data, suggest a mindful pause or deeper breath.
3. Compare their current state to their historical average with kindness and wisdom.
4. Calm, gentle, and supportive.
"""
}

async def ask_llm_async(fitness_summary: str, user_message: str = None, persona: str = "general") -> str:
    system_prompt = PERSONA_PROMPTS.get(persona, SYSTEM_PROMPT)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Fitness summary:{fitness_summary}\nUser message: {user_message}"
        }
    ]

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.6
    )

    return response.choices[0].message.content.strip()

async def stream_llm_async(fitness_summary: str, user_message: str = None, persona: str = "general") -> AsyncGenerator[str, None]:
    system_prompt = PERSONA_PROMPTS.get(persona, SYSTEM_PROMPT)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Fitness summary:{fitness_summary}\nUser message: {user_message}"
        }
    ]

    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.6,
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
