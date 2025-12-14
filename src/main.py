import cv2
import mediapipe as mp
import threading
import os
import time
import requests

# Camera & Pose
from camera.webcam import open_camera, read_frame, release_camera
from pose.pose_detector import detect_pose
from pose.angle_calculator import calculate_angle

# Utils
from utils.helpers import draw_text_with_bg

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

mp_pose = mp.solutions.pose


def main():
    cap = open_camera(0)

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
    while session.running:
        ret, frame = read_frame(cap)
        if not ret:
            break

        frame, landmarks = detect_pose(frame)

        if landmarks:
            h, w, _ = frame.shape

            def pt(lm):
                return int(lm.x * w), int(lm.y * h)

            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

            # -------------------------
            # EXERCISE LOGIC
            # -------------------------

            # SQUAT
            if ACTIVE_EXERCISE == "squat":
                knee_angle = calculate_angle(
                    pt(left_hip), pt(left_knee), pt(left_ankle)
                )
                reps = exercise.update(knee_angle)
                tracker.update_reps(reps)
                draw_text_with_bg(frame, f"Squats: {reps}", 30, 80)

                angle_sum += knee_angle
                angle_count += 1

            # PUSHUPS
            elif ACTIVE_EXERCISE == "pushup":
                elbow_angle = calculate_angle(
                    pt(left_shoulder), pt(left_elbow), pt(left_wrist)
                )
                reps = exercise.update(elbow_angle)
                tracker.update_reps(reps)
                draw_text_with_bg(frame, f"Push-ups: {reps}", 30, 80)

            # HIGH KNEES
            elif ACTIVE_EXERCISE == "high_knees":
                reps = exercise.update(True, False)
                tracker.update_reps(reps)
                draw_text_with_bg(frame, f"High Knees: {reps}", 30, 80)

            # PLANK (TIME BASED)
            elif ACTIVE_EXERCISE == "plank":
                body_angle = calculate_angle(
                    pt(left_shoulder), pt(left_hip), pt(left_ankle)
                )
                seconds = exercise.update(body_angle)
                tracker.update_time(seconds)
                draw_text_with_bg(frame, f"Plank: {seconds}s", 30, 80)

            # CHAIR POSE (TIME BASED)
            elif ACTIVE_EXERCISE == "chair_pose":
                knee_angle = calculate_angle(
                    pt(left_hip), pt(left_knee), pt(left_ankle)
                )
                seconds = exercise.update(knee_angle)
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
                seconds = exercise.update(
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
            requests.post(
                "http://127.0.0.1:8000/workouts/save",
                json={
                    "exercise": ACTIVE_EXERCISE,
                    "reps": reps,
                    "duration": duration,
                    "avg_angle": avg_angle
                },
                headers={
                    "Authorization": f"Bearer {USER_TOKEN}"
                }
            )

    release_camera(cap)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
