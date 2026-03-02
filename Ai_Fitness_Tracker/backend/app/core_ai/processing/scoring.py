class ScoringEngine:
    def __init__(self):
        self.feedback_cooldown = 3.0
        self.last_feedback_time = 0

        # Error severity (important!)
        self.error_weights = {
            0: 0,   # correct
            1: 20,  # shallow
            2: 25,  # forward lean
            3: 30,  # knees cave
            4: 25,  # heels up
            5: 20   # asymmetry
        }

    def calculate_score(self, exercise_name, features, ml_result):
        """
        Hybrid scoring: ML + Rules
        """

        score = 100.0
        feedback = []

        # ---------------------------
        # 1. ML-BASED SCORING
        # ---------------------------
        pred_class = ml_result.get("class", 0)
        confidence = ml_result.get("confidence", 1.0)

        deduction = self.error_weights.get(pred_class, 20) * confidence
        score -= deduction

        # Add ML feedback
        if pred_class != 0:
            feedback.append(ml_result.get("feedback"))

        # ---------------------------
        # 2. RULE-BASED VALIDATION
        # ---------------------------

        # 🔹 Depth check (CRITICAL)
        knee_avg = (features.get('left_knee_angle', 180) +
                    features.get('right_knee_angle', 180)) / 2

        if knee_avg > 120:
            score -= 10
            feedback.append("Go deeper in squat")

        # 🔹 Torso lean
        torso_lean = features.get('torso_lean', 0)
        if torso_lean > 40:
            score -= 10
            feedback.append("Keep chest up")

        # 🔹 Knee alignment
        knee_lat = abs(features.get('left_knee_lateral', 0)) + \
                   abs(features.get('right_knee_lateral', 0))

        if knee_lat > 0.15:
            score -= 10
            feedback.append("Push knees outward")

        # 🔹 Symmetry
        symmetry = features.get('symmetry_score', 1.0)
        if symmetry < 0.7:
            score -= 10
            feedback.append("Maintain balance")

        # ---------------------------
        # FINAL SCORE
        # ---------------------------
        score = max(0, min(100, score))

        # Remove duplicates
        feedback = list(set(feedback))

        return score, feedback

    async def get_llm_feedback(self, exercise_name, score, rule_feedback, features):
        try:
            from ..coach.llm_coach import ask_llm_async
        except Exception:
            try:
                from backend.app.core_ai.coach.llm_coach import ask_llm_async
            except Exception:
                return None

        parts = []
        parts.append(f"Exercise: {exercise_name}")
        parts.append(f"Current posture score: {int(score)}")
        if rule_feedback:
            parts.append("Issues: " + ", ".join(rule_feedback))
        key_feats = []
        for k in ["knee_avg", "hip_avg", "spine_angle", "torso_lean", "symmetry_score", "hip_depth", "left_knee_lateral", "right_knee_lateral"]:
            if k in features:
                key_feats.append(f"{k}={round(float(features.get(k, 0)), 3)}")
        if key_feats:
            parts.append("Features: " + ", ".join(key_feats))
        summary = "\n".join(parts)

        try:
            msg = await ask_llm_async(summary, "Give a one-sentence corrective cue.", "general")
            return msg
        except Exception:
            return None
