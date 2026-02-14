import time

class Plank:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0
        self.feedback = {}

    def update(self, body_angle):
        self.feedback = {}
        # body_angle ≈ shoulder–hip–ankle
        # Shoulder: 11, Hip: 23, Ankle: 27
        
        color = (0, 255, 0) if body_angle > 160 else (0, 0, 255)
        for idx in [11, 23, 27]:
            self.feedback[idx] = color

        if body_angle > 160:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None

        return round(self.time_held, 1), self.feedback
