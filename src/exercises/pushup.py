class PushUp:
    def __init__(self):
        self.state = "UP"
        self.reps = 0

    def update(self, elbow_angle):
        if elbow_angle < 90 and self.state == "UP":
            self.state = "DOWN"

        elif elbow_angle > 160 and self.state == "DOWN":
            self.reps += 1
            self.state = "UP"

        return self.reps
