import cv2
import mediapipe as mp
import numpy as np
import os
import time
import requests
from enum import Enum

# Tasks API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Constants
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"
MODEL_FILENAME = "pose_landmarker_heavy.task"

# Define PoseLandmark Enum (0-32)
class PoseLandmark(Enum):
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

# Define Connections
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
]

# Initialize Landmarker
model_path = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Global state
landmarker = None
last_timestamp_ms = 0

def download_model():
    if not os.path.exists(model_path):
        print(f"Downloading pose model from {MODEL_URL}...")
        try:
            response = requests.get(MODEL_URL)
            with open(model_path, "wb") as f:
                f.write(response.content)
            print("Model downloaded successfully.")
        except Exception as e:
            print(f"Failed to download model: {e}")
            raise e

def get_landmarker():
    global landmarker
    if landmarker is None:
        if not os.path.exists(model_path):
             download_model()
            
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO
        )
        landmarker = PoseLandmarker.create_from_options(options)
    return landmarker

def detect_pose(frame, draw=True, joint_colors=None):
    global last_timestamp_ms
    detector = get_landmarker()
    
    # Convert to RGB and mp Image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect (VIDEO mode requires strictly increasing timestamp)
    timestamp_ms = int(time.time() * 1000)
    if timestamp_ms <= last_timestamp_ms:
        timestamp_ms = last_timestamp_ms + 1
    last_timestamp_ms = timestamp_ms
    
    detection_result = detector.detect_for_video(mp_image, timestamp_ms)
    
    landmarks_list = detection_result.pose_landmarks
    
    landmarks = None
    if landmarks_list:
        landmarks = landmarks_list[0] # First person
        
        if draw:
            h, w, _ = frame.shape
            
            # Draw Connections
            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    lm1 = landmarks[start_idx]
                    lm2 = landmarks[end_idx]
                    x1, y1 = int(lm1.x * w), int(lm1.y * h)
                    x2, y2 = int(lm2.x * w), int(lm2.y * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            # Draw Landmarks
            for idx, lm in enumerate(landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                color = (0, 255, 0)
                if joint_colors and idx in joint_colors:
                    color = joint_colors[idx]
                
                cv2.circle(frame, (cx, cy), 4, color, -1)
                
                if joint_colors and idx in joint_colors:
                     cv2.circle(frame, (cx, cy), 10, color, 2)

    return frame, landmarks
