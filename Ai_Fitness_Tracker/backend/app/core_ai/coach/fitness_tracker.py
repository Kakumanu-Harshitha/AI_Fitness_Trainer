import time

class FitnessTracker:
    def __init__(self, exercise_name):
        self.exercise = exercise_name
        self.start_time = time.time()
        self.total_frames = 0
        self.good_frames = 0
        self.bad_frames = 0
        self.angle_sum = 0
        self.angle_count = 0
        self.reps = 0
        self.time_held = 0.0
        self.calories_burned = 0.0
        self.posture_history = []
        self.rep_times = []
        self.last_rep_time = time.time()
        
        # MET values (Metabolic Equivalent of Task)
        self.met_values = {
            "squat": 5.0,
            "pushup": 8.0,
            "plank": 3.0,
            "high_knees": 10.0,
            "chair_pose": 3.0,
            "tree_pose": 2.5
        }

    def update_calories(self, duration_sec, intensity=1.0):
        """
        Updates calories based on MET * weight_kg * duration_hr
        Assume average weight 70kg for now.
        intensity: multiplier based on speed/velocity (Feature 6)
        """
        met = self.met_values.get(self.exercise, 3.0)
        weight_kg = 70.0
        duration_hr = (duration_sec / 3600.0)
        
        # DL-Based Improvement: Adjust MET based on intensity
        adjusted_met = met * intensity
        
        # We only add the incremental calories for this update period
        # But usually, it's easier to calculate total at the end.
        # Let's just store it for the summary.
        self.calories_burned = adjusted_met * weight_kg * duration_hr

    def update_reps(self, reps):
        if reps > self.reps:
            now = time.time()
            self.rep_times.append(now - self.last_rep_time)
            self.last_rep_time = now
        self.reps = reps

    def update_time(self, seconds):
        self.time_held = seconds

    def update_posture_score(self, score):
        """score: 1.0 for good, 0.0 for bad"""
        self.posture_history.append(score)
        if len(self.posture_history) > 100:
            self.posture_history.pop(0)

    def summary(self):
        avg_angle = self.angle_sum / self.angle_count if self.angle_count else 0
        posture_quality = (
            (sum(self.posture_history) / len(self.posture_history)) * 100
            if self.posture_history else 0
        )
        
        avg_rep_speed = (sum(self.rep_times) / len(self.rep_times)) if self.rep_times else 0

        return {
            "exercise": self.exercise,
            "reps": self.reps,
            "time_held_sec": round(self.time_held, 1),
            "average_angle": round(avg_angle, 1),
            "posture_quality_percent": round(posture_quality, 1),
            "avg_rep_speed_sec": round(avg_rep_speed, 1),
            "calories_burned": round(self.calories_burned, 2),
            "active_time_sec": int(time.time() - self.start_time)
        }
