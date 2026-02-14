class PushUp:
    def __init__(self):
        self.state = "UP"
        self.reps = 0
        self.feedback = {}

    def update(self, elbow_angle):
        self.feedback = {}
        color = (0, 255, 0)
        
        # Shoulder: 11, Elbow: 13, Wrist: 15
        if elbow_angle < 60: # Too deep/collapsed
            color = (0, 0, 255)
            
        for idx in [11, 13, 15]:
            self.feedback[idx] = color

        if elbow_angle < 90 and self.state == "UP":
            self.state = "DOWN"

        elif elbow_angle > 160 and self.state == "DOWN":
            self.reps += 1
            self.state = "UP"

        return self.reps, self.feedback
