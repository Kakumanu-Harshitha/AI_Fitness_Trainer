import pickle
import numpy as np
import os
import pandas as pd

class MLModelLayer:
    def __init__(self, model_path=None):
        self.model = None

        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "squat_classifier.pkl")

        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✅ ML Model loaded from {model_path}")
            except Exception as e:
                print(f"❌ Failed to load ML model: {e}")
        else:
            print(f"❌ Model not found at {model_path}")

        # -------- LABEL MAP --------
        self.label_map = {
            0: "Correct squat",
            1: "Shallow squat",
            2: "Forward lean",
            3: "Knees caving in",
            4: "Heels off ground",
            5: "Asymmetric squat"
        }

        # -------- FEEDBACK MAP --------
        self.feedback_map = {
            0: "Good form. Keep going!",
            1: "Go deeper in your squat.",
            2: "Keep your back straight.",
            3: "Push your knees outward.",
            4: "Keep your heels on the ground.",
            5: "Maintain body balance."
        }

        # -------- SCORE MAP --------
        self.score_map = {
            0: 95,
            1: 70,
            2: 60,
            3: 50,
            4: 55,
            5: 65
        }

        # -------- IMPORTANT: UPDATED FEATURE SET --------
        self.feature_cols = [
            'knee_avg',
            'hip_avg',
            'spine_angle',
            'torso_lean',
            'symmetry_score',
            'hip_depth',
            'left_knee_lateral',
            'right_knee_lateral'
        ]

    def predict(self, exercise_name, features):
        """
        Returns:
        {
            class, label, confidence, score, feedback
        }
        """

        if not self.model or exercise_name != "squat":
            return {
                "class": 0,
                "label": "Fallback",
                "confidence": 1.0,
                "score": 85.0,
                "feedback": "Model not loaded"
            }

        try:
            # -------- BUILD INPUT --------
            row_data = [features.get(col, 0) for col in self.feature_cols]
            X = pd.DataFrame([row_data], columns=self.feature_cols).astype(np.float32)

            # -------- PREDICTION --------
            probs = self.model.predict_proba(X)[0]
            pred_class = int(self.model.predict(X)[0])
            confidence = float(np.max(probs))

            # -------- MAP OUTPUT --------
            label = self.label_map.get(pred_class, "Unknown")
            feedback = self.feedback_map.get(pred_class, "Adjust your form")
            base_score = self.score_map.get(pred_class, 60)

            # -------- SMART SCORING --------
            score = base_score * confidence + (1 - confidence) * 50
            score = max(0, min(100, score))

            # -------- DEBUG LOG --------
            print("\n" + "="*50)
            print(" 🤖 ML INFERENCE (FINAL)")
            print("="*50)
            print(f" Class: {pred_class} → {label}")
            print(f" Confidence: {confidence:.2f}")
            print(f" Score: {score:.2f}")
            print("- Features:")
            for col, val in zip(self.feature_cols, row_data):
                print(f"   {col}: {val:.2f}")
            print("="*50 + "\n")

            return {
                "class": pred_class,
                "label": label,
                "confidence": confidence,
                "score": score,
                "feedback": feedback
            }

        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return {
                "class": 0,
                "label": "Error",
                "confidence": 0.0,
                "score": 80.0,
                "feedback": "Prediction failed"
            }

    # -------- OPTIONAL: LIGHTWEIGHT EXERCISE DETECTION --------
    def predict_exercise(self, features):
        """
        Simple heuristic (edge-friendly)
        """
        knee = features.get("knee_avg", 180)
        elbow = features.get("left_elbow_angle", 180)

        if knee < 120:
            return "squat", 0.9
        elif elbow < 120:
            return "pushup", 0.9
        else:
            return "unknown", 0.5