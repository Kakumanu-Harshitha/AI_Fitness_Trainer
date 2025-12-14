import cv2
import mediapipe as mp


# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def detect_pose(frame):
    """
    Takes a BGR frame, detects pose landmarks,
    draws skeleton, and returns landmarks.
    """

    # Convert BGR (OpenCV) to RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = pose.process(rgb_frame)

    landmarks = None

    # If pose is detected
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Draw skeleton on the frame
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    return frame, landmarks
