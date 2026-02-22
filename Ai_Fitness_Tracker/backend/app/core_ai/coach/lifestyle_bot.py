import os
from groq import AsyncGroq
from dotenv import load_dotenv
from typing import AsyncGenerator, Dict, Any

load_dotenv()

# Initialize Groq client
try:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Groq client init error: {e}")
    client = None

SYSTEM_PROMPT_TEMPLATE = """
You are an expert AI Fitness & Lifestyle Coach dedicated to helping {username} achieve their peak potential.
Your responses must be highly personalized based on the user's specific profile and goals.

USER PROFILE:
- Age: {age} | Height: {height_cm}cm | Weight: {weight_kg}kg
- Body Type: {body_type} (Tailor advice to this somatotype)
- Activity Level: {activity_level}
- Main Goal: {diet_goal}
- Daily Targets: Sleep {daily_sleep_goal}h | Water {daily_water_goal}ml
- Injuries/Conditions: {injuries} (CRITICAL: Avoid recommending exercises that aggravate these)
- Dietary Preferences: {dietary_preferences}

GUIDELINES:
1. **Context-Aware**: Always reference their specific data (e.g., "Since you're an Endomorph looking to lose weight...").
2. **Safety First**: If they have injuries ({injuries}), strictly warn against harmful movements and suggest safe alternatives.
3. **Dietary Adherence**: Respect their preferences ({dietary_preferences}) in all food recommendations.
4. **Tone**: Encouraging, professional, and knowledgeable.
5. **Conciseness**: Keep answers under 4 sentences unless asked for a detailed plan.

If the user asks a question unrelated to fitness/health, politely steer them back to your expertise.
"""

import json

async def generate_diet_plan(user_context: Dict[str, Any], stats_summary: Dict[str, Any]) -> Dict[str, str]:
    if not client:
        return {
            "pre_workout": "Not available",
            "post_workout": "Not available",
            "analysis": "LLM client not initialized",
            "management_suggestion": "Please check API configuration"
        }

    prompt = f"""
    You are an expert Sports Nutritionist.
    
    USER PROFILE:
    - Age: {user_context.get("age", "N/A")} | Height: {user_context.get("height_cm", "N/A")}cm | Weight: {user_context.get("weight_kg", "N/A")}kg
    - Body Type: {user_context.get("body_type", "N/A")}
    - Activity Level: {user_context.get("activity_level", "N/A")}
    - Main Goal: {user_context.get("diet_goal", "N/A")}
    - Dietary Preferences: {user_context.get("dietary_preferences", "None")}
    - Injuries: {user_context.get("injuries", "None")}
    
    RECENT PERFORMANCE (Today):
    - Workout Duration: {stats_summary.get("minutes", 0)} mins
    - Calories Burned: {stats_summary.get("calories", 0)} kcal
    
    TASK:
    Generate a concise diet plan JSON with 4 keys:
    1. "pre_workout": Specific food/drink recommendation before workout.
    2. "post_workout": Specific food/drink recommendation after workout.
    3. "analysis": Brief analysis of how their diet should align with their body type and goal.
    4. "management_suggestion": Tips on timing and portion control.
    
    OUTPUT FORMAT:
    Return ONLY valid JSON. No markdown formatting.
    Example:
    {{
        "pre_workout": "Banana and almond butter",
        "post_workout": "Whey protein shake with oats",
        "analysis": "As an Ectomorph...",
        "management_suggestion": "Eat every 3 hours..."
    }}
    """

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a nutritionist API that outputs only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        print(f"Diet Plan Error: {e}")
        return {
            "pre_workout": "Complex carbs (oats/toast) 1-2h before",
            "post_workout": "Protein + fast carbs immediately after",
            "analysis": "Focus on whole foods and hydration.",
            "management_suggestion": "Track macros if possible."
        }

async def ask_lifestyle_bot(user_context: Dict[str, Any], user_message: str) -> str:
    if not client:
        return "I'm currently offline (API Key missing). Please check system configuration."

    # Format the system prompt with user data
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        username=user_context.get("username", "Athlete"),
        age=user_context.get("age", "N/A"),
        height_cm=user_context.get("height_cm", "N/A"),
        weight_kg=user_context.get("weight_kg", "N/A"),
        body_type=user_context.get("body_type", "N/A"),
        activity_level=user_context.get("activity_level", "N/A"),
        diet_goal=user_context.get("diet_goal", "N/A"),
        daily_sleep_goal=user_context.get("daily_sleep_goal", "N/A"),
        daily_water_goal=user_context.get("daily_water_goal", "N/A"),
        injuries=user_context.get("injuries") or "None",
        dietary_preferences=user_context.get("dietary_preferences") or "None"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again later."
