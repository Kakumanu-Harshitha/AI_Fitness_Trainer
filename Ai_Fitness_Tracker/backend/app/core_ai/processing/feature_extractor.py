import numpy as np

class FeatureExtractor:
    def __init__(self):
        pass

    def to_np(self, lm):
        return np.array([lm.x, lm.y]) if lm else None

    def calculate_angle(self, a, b, c):
        if a is None or b is None or c is None:
            return 0.0

        a, b, c = self.to_np(a), self.to_np(b), self.to_np(c)

        ba = a - b
        bc = c - b

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba == 0 or norm_bc == 0:
            return 0.0

        cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
        cosine = np.clip(cosine, -1.0, 1.0)

        return np.degrees(np.arccos(cosine))

    def extract_features(self, landmarks):
        if not landmarks:
            return {}

        def get_lm(idx):
            return landmarks[idx] if idx < len(landmarks) else None

        features = {}

        # ----------- JOINT ANGLES -----------
        l_sh, r_sh = get_lm(11), get_lm(12)
        l_hip, r_hip = get_lm(23), get_lm(24)
        l_knee, r_knee = get_lm(25), get_lm(26)
        l_ankle, r_ankle = get_lm(27), get_lm(28)

        features['left_knee_angle'] = self.calculate_angle(l_hip, l_knee, l_ankle)
        features['right_knee_angle'] = self.calculate_angle(r_hip, r_knee, r_ankle)

        features['left_hip_angle'] = self.calculate_angle(l_sh, l_hip, l_knee)
        features['right_hip_angle'] = self.calculate_angle(r_sh, r_hip, r_knee)

        # ----------- AGGREGATED (IMPORTANT FOR ML) -----------
        features['knee_avg'] = (features['left_knee_angle'] + features['right_knee_angle']) / 2
        features['hip_avg'] = (features['left_hip_angle'] + features['right_hip_angle']) / 2

        # ----------- BODY NORMALIZATION -----------
        def dist(a, b):
            if a is None or b is None:
                return 0.0
            return np.linalg.norm(self.to_np(a) - self.to_np(b))

        shoulder_width = dist(l_sh, r_sh)
        hip_width = dist(l_hip, r_hip)
        torso_length = dist(l_sh, l_hip)

        features['shoulder_width'] = shoulder_width
        features['hip_width'] = hip_width
        features['torso_length'] = torso_length

        # Avoid divide-by-zero
        norm_factor = torso_length if torso_length > 0 else 1.0

        # ----------- SPINE / POSTURE -----------
        if l_sh and l_hip:
            spine_vec = self.to_np(l_sh) - self.to_np(l_hip)
            vertical = np.array([0, -1])
            cosine = np.dot(spine_vec, vertical) / (np.linalg.norm(spine_vec) + 1e-6)
            cosine = np.clip(cosine, -1.0, 1.0)
            spine_angle = np.degrees(np.arccos(cosine))
        else:
            spine_angle = 0.0

        features['spine_angle'] = spine_angle
        features['torso_lean'] = spine_angle / 90.0  # normalized

        # ----------- KNEE ALIGNMENT -----------
        if l_knee and l_ankle:
            features['left_knee_lateral'] = (l_knee.x - l_ankle.x) / norm_factor
        else:
            features['left_knee_lateral'] = 0.0

        if r_knee and r_ankle:
            features['right_knee_lateral'] = (r_knee.x - r_ankle.x) / norm_factor
        else:
            features['right_knee_lateral'] = 0.0

        # ----------- SYMMETRY -----------
        features['symmetry_score'] = abs(features['left_knee_angle'] - features['right_knee_angle'])

        # ----------- HIP DEPTH (CRITICAL FOR SQUATS) -----------
        if l_hip and l_knee:
            features['hip_depth'] = (l_hip.y - l_knee.y) / norm_factor
        else:
            features['hip_depth'] = 0.0

        return features