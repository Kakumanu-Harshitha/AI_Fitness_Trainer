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

FORMATTED_PLAN_INSTRUCTIONS = """
You are an AI fitness coach integrated into a modern fitness application.

Your response MUST be clean, structured, and easy to display in a UI.
DO NOT write long paragraphs.
DO NOT return plain text blocks.

FORMAT YOUR RESPONSE STRICTLY LIKE THIS:

### 🏋️ Workout Plan
- Warm-up: (short description)
- Main Exercises:
  - Exercise 1 (sets x reps)
  - Exercise 2 (sets x reps)
- Cool-down: (short description)

### 🥗 Diet Plan
- Breakfast: (short)
- Lunch: (short)
- Dinner: (short)
- Snacks: (optional)

### 💧 Hydration
- Daily Water Intake: (in liters)
- Tips: (1–2 short points)

### 📊 Explanation
- 2–3 short bullet points explaining WHY this plan suits the user

RULES:
- Use bullet points ONLY (no paragraphs)
- Keep each line SHORT (max 1 sentence)
- Use simple, clean language
- No unnecessary text
- No markdown errors
- No extra headings
- No emojis except the section headers above
"""

async def ask_coach_formatted(user_context: Dict[str, Any], preds: Dict[str, Any], user_query: str) -> str:
    if not client:
        # Minimal deterministic fallback in case LLM is unavailable
        water_l = preds.get("water", 2.5)
        return (
            "### 🏋️ Workout Plan\n"
            "- Warm-up: 5 min brisk walk + mobility\n"
            "- Main Exercises:\n"
            "  - Bike HIIT 8×(30s hard/60s easy)\n"
            "  - Leg press 3×12\n"
            "  - Bodyweight squats 3×12\n"
            "- Cool-down: 5 min easy spin + stretches\n\n"
            "### 🥗 Diet Plan\n"
            "- Breakfast: Greek yogurt, berries, oats\n"
            "- Lunch: Chicken, quinoa, mixed greens\n"
            "- Dinner: Salmon, veggies, sweet potato\n"
            "- Snacks: Cottage cheese, apple\n\n"
            "### 💧 Hydration\n"
            f"- Daily Water Intake: {round(float(water_l),2)} L\n"
            "- Tips: Sip evenly; add electrolytes for HIIT\n\n"
            "### 📊 Explanation\n"
            "- Matches goals and current fitness level\n"
            "- Balances HIIT and strength safely\n"
            "- High protein supports recovery\n"
        )

    formatted_user = {
        "username": user_context.get("username"),
        "age": user_context.get("age"),
        "height_cm": user_context.get("height_cm"),
        "weight_kg": user_context.get("weight_kg"),
        "body_type": user_context.get("body_type"),
        "activity_level": user_context.get("activity_level"),
        "diet_goal": user_context.get("diet_goal"),
        "daily_sleep_goal": user_context.get("daily_sleep_goal"),
        "daily_water_goal": user_context.get("daily_water_goal"),
        "injuries": user_context.get("injuries"),
        "dietary_preferences": user_context.get("dietary_preferences"),
    }

    prompt = (
        FORMATTED_PLAN_INSTRUCTIONS
        + "\n\nUSER DATA:\n"
        + str(formatted_user)
        + "\n\nMODEL OUTPUT:\n"
        + f"- Calories: {preds.get('calories')}\n"
        + f"- Water: {preds.get('water')}\n"
        + f"- Intensity: {preds.get('intensity')}\n"
        + "\nUSER QUERY:\n"
        + user_query
    )

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Return ONLY the specified markdown sections and bullets."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Formatted Error: {e}")
        return "### 🏋️ Workout Plan\n- Warm-up: 5 min brisk walk\n- Main Exercises:\n  - Bodyweight squats 3×12\n  - Lunges 3×10/leg\n- Cool-down: stretches\n\n### 🥗 Diet Plan\n- Breakfast: Yogurt + oats\n- Lunch: Chicken + quinoa\n- Dinner: Fish + veggies\n- Snacks: Fruit\n\n### 💧 Hydration\n- Daily Water Intake: 2.5 L\n- Tips: Sip evenly; add electrolytes\n\n### 📊 Explanation\n- Simple, safe starter plan\n- Supports fat loss and recovery\n- Matches experience level\n"
