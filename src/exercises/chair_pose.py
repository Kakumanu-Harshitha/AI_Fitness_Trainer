import time


class ChairPose:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0

    def update(self, knee_angle):
        """
        Counts time only when chair pose is correct
        """

        if 90 <= knee_angle <= 120:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None  # pause timer

        return round(self.time_held, 1)
