import time
import numpy as np

class Meditation:
    def __init__(self):
        self.start_time = None
        self.last_breath_time = time.time()
        self.breath_count = 0
        self.shoulder_y_history = []
        self.posture_score = 100
        self.is_meditating = False
        self.feedback = "Sit comfortably and breathe deeply."

    def update(self, landmarks):
        """
        landmarks: List of (x, y, z, visibility) from MediaPipe Pose
        """
        # Landmarks: 11 (Left Shoulder), 12 (Right Shoulder), 0 (Nose)
        l_shoulder = landmarks[11]
        r_shoulder = landmarks[12]
        nose = landmarks[0]
        
        # 1. Check if user is present and reasonably centered
        if l_shoulder.visibility < 0.5 or r_shoulder.visibility < 0.5:
            self.feedback = "Please sit in front of the camera."
            return {
                "is_meditating": False,
                "breath_rate": 0,
                "posture_score": 0,
                "feedback": self.feedback
            }

        # 2. Track Shoulder Movement for Breath Detection
        avg_shoulder_y = (l_shoulder.y + r_shoulder.y) / 2
        self.shoulder_y_history.append(avg_shoulder_y)
        if len(self.shoulder_y_history) > 30 * 5: # Keep last 5 seconds (assuming ~30fps)
            self.shoulder_y_history.pop(0)

        # Simple Breath Detection: Count peaks in shoulder vertical movement
        # This is a very rough approximation using variance/oscillation
        if len(self.shoulder_y_history) > 30:
            y_data = np.array(self.shoulder_y_history)
            # Normalize
            y_data = y_data - np.mean(y_data)
            # Count zero crossings (approx breaths)
            zero_crossings = np.where(np.diff(np.sign(y_data)))[0]
            # Each full cycle (inhale+exhale) has 2 crossings. 
            # Breath rate per minute = (crossings / 2) * (60 / duration_in_seconds)
            duration = len(self.shoulder_y_history) / 30 # seconds
            if duration > 0:
                self.breath_count = int((len(zero_crossings) / 2) * (60 / duration))

        # 3. Posture/Stillness Check
        # Calculate standard deviation of nose position to measure stillness
        if not self.start_time:
            self.start_time = time.time()
            
        current_time = time.time()
        session_duration = current_time - self.start_time

        # If movement is low, score is high
        if len(self.shoulder_y_history) > 10:
            movement = np.std(self.shoulder_y_history[-10:]) # last ~0.3s
            if movement < 0.002: # Very still
                self.posture_score = min(100, self.posture_score + 0.5)
                self.feedback = "Excellent stillness. Focus on your breath."
            elif movement < 0.01: # Normal breathing
                self.posture_score = min(100, self.posture_score + 0.1)
                self.feedback = "Good. Breathe deeply."
            else: # Moving too much
                self.posture_score = max(0, self.posture_score - 1.0)
                self.feedback = "Try to remain still."

        return {
            "is_meditating": True,
            "breath_rate": self.breath_count, # Breaths per minute
            "posture_score": int(self.posture_score),
            "duration": int(session_duration),
            "feedback": self.feedback
        }
