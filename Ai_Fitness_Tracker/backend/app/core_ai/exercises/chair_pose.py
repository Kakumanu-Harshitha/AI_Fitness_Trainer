import time


class ChairPose:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0
        self.feedback = {}

    def update(self, knee_angle):
        """
        Counts time only when chair pose is correct
        """
        self.feedback = {}
        correct = 90 <= knee_angle <= 120
        color = (0, 255, 0) if correct else (0, 0, 255)
        
        for idx in [23, 25, 27]:
            self.feedback[idx] = color

        if correct:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None  # pause timer

        return round(self.time_held, 1), self.feedback
