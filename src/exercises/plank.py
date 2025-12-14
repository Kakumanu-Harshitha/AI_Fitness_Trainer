import time

class Plank:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0

    def update(self, body_angle):
        # body_angle ≈ shoulder–hip–ankle
        if body_angle > 160:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None

        return round(self.time_held, 1)
