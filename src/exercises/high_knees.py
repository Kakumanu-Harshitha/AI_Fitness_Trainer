class HighKnees:
    def __init__(self):
        self.reps = 0
        self.last_leg = None

    def update(self, left_knee_up, right_knee_up):
        if left_knee_up and self.last_leg != "LEFT":
            self.reps += 1
            self.last_leg = "LEFT"

        elif right_knee_up and self.last_leg != "RIGHT":
            self.reps += 1
            self.last_leg = "RIGHT"

        return self.reps
