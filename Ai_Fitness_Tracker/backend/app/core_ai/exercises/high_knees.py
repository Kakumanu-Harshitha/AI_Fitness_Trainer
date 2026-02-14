class HighKnees:
    def __init__(self):
        self.reps = 0
        self.last_leg = None
        self.feedback = {}

    def update(self, left_knee_up, right_knee_up):
        self.feedback = {}
        # Left Knee: 25, Right Knee: 26
        self.feedback[25] = (0, 255, 0) if left_knee_up else (0, 0, 255)
        self.feedback[26] = (0, 255, 0) if right_knee_up else (0, 0, 255)

        if left_knee_up and self.last_leg != "LEFT":
            self.reps += 1
            self.last_leg = "LEFT"

        elif right_knee_up and self.last_leg != "RIGHT":
            self.reps += 1
            self.last_leg = "RIGHT"

        return self.reps, self.feedback
