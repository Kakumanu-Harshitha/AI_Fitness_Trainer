import math
import random

def compute_bmi(weight_kg: float, height_cm: float) -> float:
    h = max(height_cm, 1.0) / 100.0
    return round(weight_kg / (h * h), 2)

def compute_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    g = (gender or "").lower()
    if g.startswith("m"):
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

def intensity_from_experience(exp: str) -> int:
    e = (exp or "").strip().lower()
    if e.startswith("beg"):
        return 3
    if e.startswith("inter"):
        return 6
    if e.startswith("adv"):
        return 8
    return 5

def random_goal() -> str:
    return random.choice(["fat_loss", "muscle_gain", "maintenance"])

def rule_based_predictions(gender: str, age: int, height_cm: float, weight_kg: float, workout_frequency: int, session_duration: float, experience_level: str) -> dict:
    bmr = compute_bmr(gender, weight_kg, height_cm, age)
    calories = bmr * (1.2 + max(workout_frequency, 0) * 0.1)
    water = weight_kg * 0.035 + max(session_duration, 0) * 0.5
    intensity = intensity_from_experience(experience_level)
    return {
        "calories": round(calories, 2),
        "water": round(water, 2),
        "intensity": int(intensity)
    }
