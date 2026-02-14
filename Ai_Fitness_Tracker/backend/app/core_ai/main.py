import cv2
import mediapipe as mp
import threading
import os
import sys
import time
import requests

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Camera & Pose
from camera.webcam import open_camera, read_frame, release_camera
from pose.pose_detector import detect_pose, PoseLandmark
from pose.angle_calculator import calculate_angle

# Utils
from utils.helpers import draw_text_with_bg, check_lighting, check_visibility, detect_fatigue, get_wifi_strength

# Exercises
from exercises.squat import Squat
from exercises.pushup import PushUp
from exercises.plank import Plank
from exercises.tree_pose import TreePose
from exercises.chair_pose import ChairPose
from exercises.high_knees import HighKnees

# AI / Voice / Control
from coach.fitness_tracker import FitnessTracker
from controller.session_controller import SessionController
from voice.voice_loop import voice_loop

# -------------------------
# ENV
# -------------------------
ACTIVE_EXERCISE = os.getenv("ACTIVE_EXERCISE", "squat")
USER_TOKEN = os.getenv("USER_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

# mp_pose = mp.solutions.pose


import logging

# Configure logging
logging.basicConfig(
    filename='core_ai.log', 
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s'
)

def main():
    logging.info(f"Starting {ACTIVE_EXERCISE} session...")
    print(f"Starting {ACTIVE_EXERCISE} session...")
    
    try:
        cap = open_camera(0)
        
        if not cap.isOpened():
            logging.error("Could not open camera.")
            print("❌ Error: Could not open camera.")
            return
        
        logging.info("Camera initialized successfully.")
        print("✅ Camera initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to open camera: {e}")
        print(f"❌ Error: {e}")
        return
    
    cv2.namedWindow("AI Fitness Trainer", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("AI Fitness Trainer", cv2.WND_PROP_TOPMOST, 1)

    # -------------------------
    # Exercise Init
    # -------------------------
    if ACTIVE_EXERCISE == "squat":
        exercise = Squat()
    elif ACTIVE_EXERCISE == "pushup":
        exercise = PushUp()
    elif ACTIVE_EXERCISE == "plank":
        exercise = Plank()
    elif ACTIVE_EXERCISE == "tree_pose":
        exercise = TreePose()
    elif ACTIVE_EXERCISE == "chair_pose":
        exercise = ChairPose()
    elif ACTIVE_EXERCISE == "high_knees":
        exercise = HighKnees()
    else:
        raise ValueError("Invalid exercise")

    tracker = FitnessTracker(ACTIVE_EXERCISE)
    session = SessionController()

    # -------------------------
    # Voice Thread
    # -------------------------
    threading.Thread(
        target=voice_loop,
        args=(tracker, session),
        daemon=True
    ).start()

    start_time = time.time()
    angle_sum = 0
    angle_count = 0

    # -------------------------
    # CV Loop
    # -------------------------
    joint_colors = {}
    out_of_frame_start = None
    is_paused = False
    last_landmarks = None
    last_wifi_check = 0
    wifi_strength = 100
    
    while session.running:
        loop_start = time.time()
        ret, frame = read_frame(cap)
        if not ret:
            break

        # Wi-Fi Signal Awareness (Feature 1)
        if time.time() - last_wifi_check > 5.0:
            wifi_strength = get_wifi_strength()
            last_wifi_check = time.time()
        
        if wifi_strength is not None and wifi_strength < 40:
            draw_text_with_bg(frame, f"WEAK WI-FI: {wifi_strength}%", 30, 280, 0.6, (255, 255, 255), (0, 0, 150))

        frame, landmarks = detect_pose(frame, joint_colors=joint_colors)

        # Smart Workout Zone Detection
        lighting_ok = check_lighting(frame)
        if not lighting_ok:
            draw_text_with_bg(frame, "LOW LIGHTING - Turn on a light", 30, 120, 0.7, (255, 255, 255), (0, 0, 255))
            
        if landmarks:
            visible_ok, msg = check_visibility(landmarks)
            if not visible_ok:
                draw_text_with_bg(frame, f"ZONE WARNING: {msg}", 30, 160, 0.7, (255, 255, 255), (0, 0, 255))
            
            is_fatigued, f_score = detect_fatigue(landmarks)
            if is_fatigued:
                draw_text_with_bg(frame, "FATIGUE DETECTED - Take a breath!", 30, 200, 0.7, (255, 255, 255), (0, 165, 255))

        if not landmarks:
            if out_of_frame_start is None:
                out_of_frame_start = time.time()
            
            elapsed = time.time() - out_of_frame_start
            if elapsed > 2.0: # 2 seconds out of frame
                is_paused = True
            
            if is_paused:
                draw_text_with_bg(frame, "PAUSED - User out of frame", 30, 40, 0.7, (255, 255, 255), (0, 0, 255))
        else:
            out_of_frame_start = None
            if is_paused:
                is_paused = False
                # Reset start time for time-based exercises to account for the pause
                if hasattr(exercise, 'start_time') and exercise.start_time is not None:
                    exercise.start_time = time.time() - exercise.time_held

            h, w, _ = frame.shape
            joint_colors = {} # Reset for next frame

            if not is_paused:
                def pt(lm):
                    return int(lm.x * w), int(lm.y * h)

                left_hip = landmarks[PoseLandmark.LEFT_HIP.value]
                left_knee = landmarks[PoseLandmark.LEFT_KNEE.value]
                left_ankle = landmarks[PoseLandmark.LEFT_ANKLE.value]

                left_shoulder = landmarks[PoseLandmark.LEFT_SHOULDER.value]
                left_elbow = landmarks[PoseLandmark.LEFT_ELBOW.value]
                left_wrist = landmarks[PoseLandmark.LEFT_WRIST.value]

                # Calculate Intensity (Feature 6)
                intensity = 1.0
                if last_landmarks:
                    # Measure movement of hips and shoulders
                    displacement = 0
                    for i in [11, 12, 23, 24]:
                        curr = landmarks[i]
                        prev = last_landmarks[i]
                        displacement += ((curr.x - prev.x)**2 + (curr.y - prev.y)**2)**0.5
                    
                    # Normalize displacement to intensity (heuristic)
                    intensity = 1.0 + min(displacement * 10, 2.0)
                
                last_landmarks = landmarks
                
                # Update Calories
                current_duration = time.time() - start_time
                tracker.update_calories(current_duration, intensity)
                draw_text_with_bg(frame, f"Kcal: {round(tracker.calories_burned, 2)}", 30, 240, 0.7, (255, 255, 255), (100, 50, 0))

                # -------------------------
                # EXERCISE LOGIC
                # -------------------------

                # SQUAT
                if ACTIVE_EXERCISE == "squat":
                    knee_angle = calculate_angle(
                        pt(left_hip), pt(left_knee), pt(left_ankle)
                    )
                    reps, joint_colors = exercise.update(knee_angle)
                    tracker.update_reps(reps)
                    
                    # Update posture history
                    is_good = 70 <= knee_angle <= 160
                    tracker.update_posture_score(1.0 if is_good else 0.0)
                    
                    draw_text_with_bg(frame, f"Squats: {reps}", 30, 80)

                    angle_sum += knee_angle
                    angle_count += 1

                # PUSHUPS
                elif ACTIVE_EXERCISE == "pushup":
                    elbow_angle = calculate_angle(
                        pt(left_shoulder), pt(left_elbow), pt(left_wrist)
                    )
                    reps, joint_colors = exercise.update(elbow_angle)
                    tracker.update_reps(reps)
                    tracker.update_posture_score(1.0 if elbow_angle > 60 else 0.0)
                    draw_text_with_bg(frame, f"Push-ups: {reps}", 30, 80)

                # HIGH KNEES
                elif ACTIVE_EXERCISE == "high_knees":
                    # Better logic for high knees
                    left_knee_up = left_knee.y < left_hip.y
                    right_knee = landmarks[PoseLandmark.RIGHT_KNEE.value]
                    right_hip = landmarks[PoseLandmark.RIGHT_HIP.value]
                    right_knee_up = right_knee.y < right_hip.y
                    
                    reps, joint_colors = exercise.update(left_knee_up, right_knee_up)
                    tracker.update_reps(reps)
                    draw_text_with_bg(frame, f"High Knees: {reps}", 30, 80)

                # PLANK (TIME BASED)
                elif ACTIVE_EXERCISE == "plank":
                    body_angle = calculate_angle(
                        pt(left_shoulder), pt(left_hip), pt(left_ankle)
                    )
                    seconds, joint_colors = exercise.update(body_angle)
                    tracker.update_time(seconds)
                    draw_text_with_bg(frame, f"Plank: {seconds}s", 30, 80)

                # CHAIR POSE (TIME BASED)
                elif ACTIVE_EXERCISE == "chair_pose":
                    knee_angle = calculate_angle(
                        pt(left_hip), pt(left_knee), pt(left_ankle)
                    )
                    seconds, joint_colors = exercise.update(knee_angle)
                    tracker.update_time(seconds)
                    draw_text_with_bg(frame, f"Chair Pose: {seconds}s", 30, 80)

                # TREE POSE (TIME BASED)
                elif ACTIVE_EXERCISE == "tree_pose":
                    standing_leg_angle = calculate_angle(
                        pt(left_hip), pt(left_knee), pt(left_ankle)
                    )
                    raised_leg_angle = calculate_angle(
                        pt(left_hip), pt(left_knee), pt(left_wrist)
                    )
                    seconds, joint_colors = exercise.update(
                        standing_leg_angle, raised_leg_angle
                    )
                    tracker.update_time(seconds)
                    draw_text_with_bg(frame, f"Tree Pose: {seconds}s", 30, 80)

        cv2.imshow("AI Fitness Trainer", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            session.running = False

    # -------------------------
    # SAVE WORKOUT
    # -------------------------
    duration = int(time.time() - start_time)
    avg_angle = angle_sum / max(angle_count, 1)
    reps = exercise.reps if hasattr(exercise, "reps") else tracker.reps

    if reps == 0 and duration < 5:
        print("⚠️ Workout too short, not saving")
    else:
        if USER_TOKEN:
            try:
                requests.post(
                    f"{API_URL}/workouts/save",
                    json={
                        "exercise": ACTIVE_EXERCISE,
                        "reps": int(reps),
                        "duration": int(duration),
                        "avg_angle": float(avg_angle),
                        "calories": float(tracker.calories_burned)
                    },
                    headers={
                        "Authorization": f"Bearer {USER_TOKEN}"
                    },
                    timeout=5
                )
                print("✅ Workout saved successfully!")
            except Exception as e:
                print(f"❌ Failed to save workout: {e}")

    release_camera(cap)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
