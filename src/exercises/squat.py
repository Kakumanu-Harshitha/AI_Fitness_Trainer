class Squat:
    def __init__(self):
        self.state = "UP"
        self.reps = 0

    def update(self, knee_angle):
        """
        Updates squat count based on knee angle
        """
        if knee_angle < 90 and self.state == "UP":
            self.state = "DOWN"

        elif knee_angle > 160 and self.state == "DOWN":
            self.reps += 1
            self.state = "UP"

        return self.reps
