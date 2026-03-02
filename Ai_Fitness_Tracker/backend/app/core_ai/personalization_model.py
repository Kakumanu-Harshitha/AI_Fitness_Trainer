import os
from typing import Dict, Any
from joblib import load
from .utils import compute_bmi, rule_based_predictions

_MODEL_PATH = os.getenv("PERSONALIZATION_MODEL_PATH", os.path.join(os.path.dirname(__file__), "personalization_model.joblib"))
_model = None
try:
    if os.path.exists(_MODEL_PATH):
        _model = load(_MODEL_PATH)
except Exception:
    _model = None

def predict(data: Dict[str, Any]) -> Dict[str, Any]:
    gender = str(data.get("gender", "male"))
    age = int(data.get("age", 25))
    height_cm = float(data.get("height_cm", 170))
    weight_kg = float(data.get("weight_kg", 70))
    workout_frequency = int(data.get("workout_frequency", 3))
    session_duration = float(data.get("session_duration", 30))
    workout_type = str(data.get("workout_type", "general"))
    experience_level = str(data.get("experience_level", "Beginner"))
    bmi = compute_bmi(weight_kg, height_cm)
    if _model is None:
        return rule_based_predictions(gender, age, height_cm, weight_kg, workout_frequency, session_duration, experience_level)
    X = [{
        "Gender": gender,
        "Workout_Type": workout_type,
        "Experience_Level": experience_level,
        "Age": age,
        "Height": height_cm,
        "Weight": weight_kg,
        "BMI": bmi,
        "workout_frequency": workout_frequency,
        "session_duration": session_duration
    }]
    try:
        y = _model.predict(X)[0]
        return {
            "calories": float(round(y[0], 2)),
            "water": float(round(y[1], 2)),
            "intensity": int(round(y[2]))
        }
    except Exception:
        return rule_based_predictions(gender, age, height_cm, weight_kg, workout_frequency, session_duration, experience_level)
