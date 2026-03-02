import cv2
import time
import asyncio

from backend.app.core_ai.pose.pose_detector import detect_pose
from backend.app.core_ai.processing.smoother import PoseSmoother
from backend.app.core_ai.processing.feature_extractor import FeatureExtractor
from backend.app.core_ai.processing.temporal import TemporalProcessor
from backend.app.core_ai.processing.rep_counter import RepCounter
from backend.app.core_ai.processing.ml_models import MLModelLayer
from backend.app.core_ai.processing.scoring import ScoringEngine


class Pipeline:
    def __init__(self, exercise_name="squat"):
        self.exercise_name = exercise_name

        self.smoother = PoseSmoother()
        self.feature_extractor = FeatureExtractor()
        self.temporal = TemporalProcessor()
        self.ml = MLModelLayer()
        self.scorer = ScoringEngine()

        self.llm_feedback_buffer = []
        self.last_llm_time = 0

        # 🔥 IMPORTANT: use stable metric
        if exercise_name == "squat":
            self.rep_counter = RepCounter("knee_avg", 100, 160)
        elif exercise_name == "pushup":
            self.rep_counter = RepCounter("left_elbow_angle", 100, 160)
        else:
            self.rep_counter = RepCounter("knee_avg", 100, 160)

    async def process_frame_async(self, frame):

        timestamp = time.perf_counter()

        # ------------------ 1. POSE ------------------
        _, raw_landmarks = detect_pose(frame, draw=False)
        if not raw_landmarks:
            return frame, {"error": "No person detected"}

        # ------------------ 2. SMOOTH ------------------
        landmarks = self.smoother.smooth(raw_landmarks)

        # ------------------ 3. FEATURES ------------------
        features = self.feature_extractor.extract_features(landmarks)

        # 🔥 IMPORTANT: derived features
        features["knee_avg"] = (
            features.get("left_knee_angle", 0) +
            features.get("right_knee_angle", 0)
        ) / 2

        features["hip_avg"] = (
            features.get("left_hip_angle", 0) +
            features.get("right_hip_angle", 0)
        ) / 2

        # ------------------ 4. TEMPORAL ------------------
        vel, acc = self.temporal.update(features, timestamp)

        # add velocity features
        for k, v in vel.items():
            features[f"{k}_vel"] = v

        # add temporal stats (VERY IMPORTANT)
        features.update(self.temporal.get_temporal_features("knee_avg"))

        # ------------------ 5. ML ------------------
        ml_result = self.ml.predict(self.exercise_name, features)

        # ------------------ 6. SCORING ------------------
        final_score, rule_feedback = self.scorer.calculate_score(
            self.exercise_name,
            features,
            ml_result
        )

        # ------------------ 7. REP COUNT ------------------
        reps = self.rep_counter.update(features, ml_result)

        # ------------------ 8. LLM FEEDBACK ------------------
        current_time = time.time()

        if final_score < 70 and (current_time - self.last_llm_time > 5):
            asyncio.create_task(
                self._fetch_llm_feedback(final_score, rule_feedback, features)
            )
            self.last_llm_time = current_time

        # combine feedback
        combined_feedback = (
            rule_feedback +
            [ml_result.get("feedback")] +
            self.llm_feedback_buffer
        )

        # ------------------ 9. DRAW ------------------
        frame = self.draw_overlay(
            frame,
            landmarks,
            reps,
            final_score,
            combined_feedback
        )

        # ------------------ DEBUG ------------------
        print("\n" + "=" * 50)
        print(f"🔄 PIPELINE | {self.exercise_name}")
        print("=" * 50)
        print(f"Reps: {reps}")
        print(f"Score: {final_score:.1f}")
        print(f"Class: {ml_result['label']} ({ml_result['confidence']:.2f})")
        print("=" * 50)

        return frame, {
            "reps": reps,
            "score": final_score,
            "feedback": combined_feedback,
            "ml": ml_result
        }

    async def _fetch_llm_feedback(self, score, rule_feedback, features):
        try:
            feedback = await self.scorer.get_llm_feedback(
                self.exercise_name,
                score,
                rule_feedback,
                features
            )
            if feedback:
                self.llm_feedback_buffer = [feedback]
                await asyncio.sleep(4)
                self.llm_feedback_buffer = []
        except Exception as e:
            print(f"LLM Error: {e}")

    def process_frame(self, frame):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            return frame, {"error": "Use async method"}

        return loop.run_until_complete(self.process_frame_async(frame))

    # ------------------ DRAW ------------------
    def draw_overlay(self, frame, landmarks, reps, score, feedback):
        h, w, _ = frame.shape

        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # skeleton
        self.draw_line(frame, landmarks[11], landmarks[12], w, h)
        self.draw_line(frame, landmarks[11], landmarks[23], w, h)
        self.draw_line(frame, landmarks[12], landmarks[24], w, h)
        self.draw_line(frame, landmarks[23], landmarks[24], w, h)
        self.draw_line(frame, landmarks[23], landmarks[25], w, h)
        self.draw_line(frame, landmarks[25], landmarks[27], w, h)
        self.draw_line(frame, landmarks[24], landmarks[26], w, h)
        self.draw_line(frame, landmarks[26], landmarks[28], w, h)

        # UI
        cv2.rectangle(frame, (0, 0), (260, 160), (0, 0, 0), -1)

        cv2.putText(frame, f"Exercise: {self.exercise_name}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.putText(frame, f"Reps: {reps}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.putText(frame, f"Score: {int(score)}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        y = 115
        for msg in feedback[:3]:  # limit text
            cv2.putText(frame, msg, (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            y += 20

        return frame

    def draw_line(self, frame, lm1, lm2, w, h):
        x1, y1 = int(lm1.x * w), int(lm1.y * h)
        x2, y2 = int(lm2.x * w), int(lm2.y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)