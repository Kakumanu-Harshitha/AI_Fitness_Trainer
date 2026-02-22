import numpy as np

class WarriorPose:
    def __init__(self):
        self.hold_time = 0
        self.correct_pose_time = 0
        self.feedback = {}

    def update(self, landmarks):
        """
        Check Warrior II Pose.
        Landmarks:
        11-12: Shoulders
        23-24: Hips
        25-26: Knees
        27-28: Ankles
        13-14: Elbows
        15-16: Wrists
        """
        self.feedback = {}

        # 1. Check if arms are horizontal
        l_sh = landmarks[11]
        r_sh = landmarks[12]
        l_el = landmarks[13]
        r_el = landmarks[14]
        l_wr = landmarks[15]
        r_wr = landmarks[16]

        arms_ok = True
        # Y-diff between shoulder and wrist should be small
        if abs(l_sh.y - l_wr.y) > 0.1 or abs(r_sh.y - r_wr.y) > 0.1:
            arms_ok = False
            self.feedback["arms"] = "Raise arms to shoulder height"
        else:
            self.feedback["arms"] = "Good arm position"

        # 2. Check leg stance (wide stance)
        l_ank = landmarks[27]
        r_ank = landmarks[28]
        # Calculate distance between ankles
        stance_width = np.sqrt((l_ank.x - r_ank.x)**2 + (l_ank.y - r_ank.y)**2)
        
        legs_ok = True
        if stance_width < 0.4: # Arbitrary threshold based on normalized coordinates
            legs_ok = False
            self.feedback["legs"] = "Widen your stance"
        else:
            self.feedback["legs"] = "Good stance"

        # 3. Check front knee bend (Assuming left knee is front for simplicity or detect which is forward)
        # Determine which knee is "front" by checking x-coordinate relative to hips
        l_hip = landmarks[23]
        r_hip = landmarks[24]
        l_knee = landmarks[25]
        r_knee = landmarks[26]

        # Calculate knee angle: Hip -> Knee -> Ankle
        def get_angle(a, b, c):
            ba = np.array([a.x - b.x, a.y - b.y])
            bc = np.array([c.x - b.x, c.y - b.y])
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)
            return np.degrees(angle)

        l_knee_angle = get_angle(l_hip, l_knee, l_ank)
        r_knee_angle = get_angle(r_hip, r_knee, r_ank)

        # In Warrior II, one knee is ~90 degrees, other is ~180
        knee_ok = False
        if (80 < l_knee_angle < 110 and r_knee_angle > 160) or \
           (80 < r_knee_angle < 110 and l_knee_angle > 160):
            knee_ok = True
            self.feedback["knees"] = "Perfect knee bend"
        else:
            self.feedback["knees"] = "Bend front knee to 90 degrees"

        is_correct = arms_ok and legs_ok and knee_ok
        
        if is_correct:
            self.correct_pose_time += 1 # Frame count
        
        return {
            "is_correct": is_correct,
            "hold_time": self.correct_pose_time / 30, # Assuming 30fps
            "feedback": self.feedback
        }
