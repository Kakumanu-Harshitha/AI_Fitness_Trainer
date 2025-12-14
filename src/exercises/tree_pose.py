import time

class TreePose:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0

    def update(self, standing_leg_angle, raised_leg_angle):
        pose_correct = (
            standing_leg_angle > 160 and
            raised_leg_angle < 120
        )

        if pose_correct:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None

        return round(self.time_held, 1)
