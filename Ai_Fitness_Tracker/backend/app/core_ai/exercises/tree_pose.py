import time

class TreePose:
    def __init__(self):
        self.start_time = None
        self.time_held = 0.0
        self.feedback = {}

    def update(self, standing_leg_angle, raised_leg_angle):
        self.feedback = {}
        
        standing_correct = standing_leg_angle > 160
        raised_correct = raised_leg_angle < 120
        
        # Standing leg: Left Hip: 23, Left Knee: 25, Left Ankle: 27
        # Raised leg (approx): Left Hip: 23, Left Knee: 25, Left Wrist: 15 (as used in main.py)
        
        standing_color = (0, 255, 0) if standing_correct else (0, 0, 255)
        raised_color = (0, 255, 0) if raised_correct else (0, 0, 255)
        
        for idx in [23, 25, 27]:
            self.feedback[idx] = standing_color
        self.feedback[15] = raised_color

        if standing_correct and raised_correct:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                self.time_held = time.time() - self.start_time
        else:
            self.start_time = None

        return round(self.time_held, 1), self.feedback
