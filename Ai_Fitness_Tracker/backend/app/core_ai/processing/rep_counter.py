
import time

class RepCounter:
    def __init__(self, metric='knee_avg', down_threshold=100, up_threshold=160, min_frames=5):
        self.metric = metric
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.min_frames = min_frames

        self.state = "UP"
        self.reps = 0
        self.frame_count = 0

    def update(self, features, ml_result=None):
        val = features.get(self.metric, None)
        if val is None:
            return self.reps

        self.frame_count += 1

        # -------- STATE MACHINE --------
        if self.state == "UP":
            if val < self.down_threshold:
                self.state = "DOWN"

        elif self.state == "DOWN":
            if val > self.up_threshold:

                # -------- VALIDATION --------
                is_valid = True

                # 🔥 Check posture using ML
                if ml_result:
                    if ml_result["class"] != 0:  # not correct squat
                        is_valid = False

                # 🔥 Check minimum frames (avoid jitter reps)
                if self.frame_count < self.min_frames:
                    is_valid = False

                if is_valid:
                    if ml_result and ml_result.get("score", 0) > 70:
                        self.reps += 1

                self.state = "UP"
                self.frame_count = 0

        return self.reps
