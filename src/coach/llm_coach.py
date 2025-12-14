import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an AI fitness coach.
You receive structured fitness metrics.
Give short, friendly, motivating advice.
Suggest rest, posture correction, or encouragement.
Do NOT give medical advice.
Do NOT mention numbers unless helpful.
Keep responses under 2 sentences.
"""

def ask_llm(fitness_summary, user_message=None):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
                        Fitness summary:{fitness_summary}
                        User message: {user_message}
                        """
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.6
    )

    return response.choices[0].message.content.strip()
