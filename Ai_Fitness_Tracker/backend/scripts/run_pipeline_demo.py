
import cv2
import numpy as np
import sys
import os
import time
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.core_ai.pipeline import Pipeline
# from backend.app.core_ai.pose.pose_detector import PoseLandmark

class MockLandmark:
    def __init__(self, x, y, z=0.0, visibility=0.9):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

def create_mock_landmarks():
    # Create 33 landmarks (MediaPipe standard)
    landmarks = []
    for i in range(33):
        # Default: some neutral position
        landmarks.append(MockLandmark(x=0.5, y=0.5, z=0.0, visibility=0.9))
    
    # Customize for a Squat (approximate)
    # Hip (23, 24) at (0.5, 0.5)
    # Knee (25, 26) at (0.5, 0.7) -> straight legs initially
    # Ankle (27, 28) at (0.5, 0.9)
    
    # Frame 1: Standing
    landmarks[11] = MockLandmark(x=0.45, y=0.2, z=0.0, visibility=0.9) # L Shoulder
    landmarks[12] = MockLandmark(x=0.55, y=0.2, z=0.0, visibility=0.9) # R Shoulder
    landmarks[23] = MockLandmark(x=0.45, y=0.5, z=0.0, visibility=0.9) # L Hip
    landmarks[24] = MockLandmark(x=0.55, y=0.5, z=0.0, visibility=0.9) # R Hip
    landmarks[25] = MockLandmark(x=0.45, y=0.7, z=0.0, visibility=0.9) # L Knee
    landmarks[26] = MockLandmark(x=0.55, y=0.7, z=0.0, visibility=0.9) # R Knee
    landmarks[27] = MockLandmark(x=0.45, y=0.9, z=0.0, visibility=0.9) # L Ankle
    landmarks[28] = MockLandmark(x=0.55, y=0.9, z=0.0, visibility=0.9) # R Ankle
    
    return landmarks

def main():
    print("Initializing Pipeline...")
    try:
        pipeline = Pipeline("squat")
    except Exception as e:
        print(f"Failed to initialize pipeline: {e}")
        return

    print("Creating mock input...")
    # Mock image (black frame)
    image = np.zeros((640, 480, 3), dtype=np.uint8)
    
    # Mock the detect_pose function GLOBALLY or just bypass it?
    # Since we can't easily mock the import inside pipeline.py without patching,
    # let's manually run the steps here to demonstrate the flow using the pipeline's components.
    
    print("\n--- Running Pipeline Components Manually (Bypassing Camera) ---")
    
    # 1. Mock Detection
    raw_landmarks = create_mock_landmarks()
    print("1. Detection: Mocked Success")
    
    # 2. Smoothing
    smoothed_landmarks = pipeline.smoother.smooth(raw_landmarks)
    print(f"2. Smoothing: {len(smoothed_landmarks)} landmarks processed")
    
    # 3. Features
    features = pipeline.feature_extractor.extract_features(smoothed_landmarks)
    
    # --- Manually add derived features (as done in pipeline.py) ---
    features["knee_avg"] = (features.get("left_knee_angle", 0) + features.get("right_knee_angle", 0)) / 2
    features["hip_avg"] = (features.get("left_hip_angle", 0) + features.get("right_hip_angle", 0)) / 2
    
    print(f"3. Features: Extracted {len(features)} features")
    print(f"   - Knee Angles: L={features.get('left_knee_angle'):.1f}, R={features.get('right_knee_angle'):.1f}, Avg={features.get('knee_avg'):.1f}")
    
    # 4. Temporal
    start_time = time.time()
    velocities, _ = pipeline.temporal.update(features, start_time)
    print(f"4. Temporal: Calculated velocities for {len(velocities)} features")
    
    # 5. Reps (Note: RepCounter now might take ml_result too, let's check pipeline.py)
    # pipeline.py: reps = self.rep_counter.update(features, ml_result)
    # So we need ML result first.
    
    # 6. ML Inference
    print(f"6. ML Layer: Running prediction...")
    ml_result = pipeline.ml.predict("squat", features)
    print(f"   - ML Result: {ml_result}")
    
    # 5. Reps (Updated order)
    # Check RepCounter signature in pipeline.py... it passes ml_result.
    # But RepCounter.update might not need it? 
    # Let's check RepCounter.update signature if possible. 
    # Assuming pipeline.py is correct: reps = self.rep_counter.update(features, ml_result)
    try:
        reps = pipeline.rep_counter.update(features, ml_result)
    except TypeError:
         # Fallback if RepCounter.update doesn't accept ml_result yet
        reps = pipeline.rep_counter.update(features, start_time)
        
    print(f"5. Reps: Current count = {reps}")
    
    # 7. Scoring
    # pipeline.py: final_score, rule_feedback = self.scorer.calculate_score(self.exercise_name, features, ml_result)
    final_score, feedback = pipeline.scorer.calculate_score("squat", features, ml_result)
    
    print(f"7. Scoring: Final Score = {final_score:.1f}")
    print(f"   - Feedback: {feedback}")
    
    # final_score is already calculated in scorer now?
    # pipeline.py shows scorer returning final_score.
    print(f"8. Final Output: Score = {final_score:.1f}")

if __name__ == "__main__":
    main()
