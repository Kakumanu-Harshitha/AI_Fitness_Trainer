class Squat:
    def __init__(self):
        self.state = "UP"
        self.reps = 0
        self.feedback = {} # landmark_idx: (B, G, R)

    def update(self, knee_angle):
        """
        Updates squat count based on knee angle
        """
        # MediaPipe indices for squat: 
        # Left Hip: 23, Left Knee: 25, Left Ankle: 27
        # Right Hip: 24, Right Knee: 26, Right Ankle: 28
        
        self.feedback = {}
        
        # Color the joints involved in the angle calculation
        # If angle is too small or too large in a bad way, color red
        # For now, just color them green if they are being tracked
        color = (0, 255, 0) # Green
        
        # Simple rule: if you are too low, maybe it's bad? 
        # Actually, let's just use red for "incorrect" form if we had more rules.
        # For now, let's say if knee_angle < 70, it might be too deep for some.
        if knee_angle < 70:
            color = (0, 0, 255) # Red
            
        for idx in [23, 25, 27]:
            self.feedback[idx] = color

        if knee_angle < 90 and self.state == "UP":
            self.state = "DOWN"

        elif knee_angle > 160 and self.state == "DOWN":
            self.reps += 1
            self.state = "UP"

        return self.reps, self.feedback
