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

    def update_angle(self, angle, min_angle, max_angle):
        self.total_frames += 1
        self.angle_sum += angle
        self.angle_count += 1

        if min_angle <= angle <= max_angle:
            self.good_frames += 1
        else:
            self.bad_frames += 1

    def update_reps(self, reps):
        self.reps = reps

    def update_time(self, seconds):
        self.time_held = seconds

    def summary(self):
        avg_angle = self.angle_sum / self.angle_count if self.angle_count else 0
        posture_quality = (
            (self.good_frames / self.total_frames) * 100
            if self.total_frames else 0
        )

        return {
            "exercise": self.exercise,
            "reps": self.reps,
            "time_held_sec": round(self.time_held, 1),
            "average_angle": round(avg_angle, 1),
            "bad_posture_frames": self.bad_frames,
            "posture_quality_percent": round(posture_quality, 1),
            "active_time_sec": int(time.time() - self.start_time)
        }
