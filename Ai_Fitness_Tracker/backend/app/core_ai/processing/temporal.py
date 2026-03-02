import numpy as np
from collections import deque

class TemporalProcessor:
    def __init__(self, buffer_size=30, smooth_window=5):
        self.buffer_size = buffer_size
        self.smooth_window = smooth_window

        self.history = deque(maxlen=buffer_size)
        self.vel_history = deque(maxlen=buffer_size)

        self.velocities = {}
        self.accelerations = {}

        self.prev_time = None

    def update(self, features, timestamp):
        if not features:
            return {}, {}

        # ----------- STABLE DT ----------- #
        if self.prev_time is None:
            self.prev_time = timestamp
            dt = 0.033
        else:
            dt = max(timestamp - self.prev_time, 1e-3)
            self.prev_time = timestamp

        self.history.append(features)

        if len(self.history) < self.smooth_window:
            return {}, {}

        # ----------- VELOCITY (WINDOW BASED) ----------- #
        velocities = {}

        old = self.history[0]
        new = self.history[-1]

        for key in features:
            dv = new.get(key, 0) - old.get(key, 0)
            velocities[key] = dv / dt

        self.vel_history.append(velocities)

        # ----------- SMOOTH VELOCITY ----------- #
        smoothed_vel = {}
        for key in velocities:
            vals = [v.get(key, 0) for v in self.vel_history]
            smoothed_vel[key] = np.mean(vals)

        # ----------- ACCELERATION ----------- #
        accelerations = {}
        if len(self.vel_history) >= 2:
            prev = self.vel_history[-2]

            for key in smoothed_vel:
                dv = smoothed_vel[key] - prev.get(key, 0)
                accelerations[key] = dv / dt
        else:
            accelerations = {k: 0.0 for k in smoothed_vel}

        self.velocities = smoothed_vel
        self.accelerations = accelerations

        return smoothed_vel, accelerations

    # ----------- 🔥 IMPORTANT FOR ML ----------- #
    def get_temporal_features(self, feature_name):
        """
        Returns ML-ready temporal features
        """
        if len(self.history) < 5:
            return {}

        values = [f.get(feature_name, 0) for f in self.history]

        arr = np.array(values, dtype=np.float32)

        return {
            f"{feature_name}_mean": float(arr.mean()),
            f"{feature_name}_std": float(arr.std()),
            f"{feature_name}_min": float(arr.min()),
            f"{feature_name}_max": float(arr.max()),
            f"{feature_name}_range": float(arr.max() - arr.min()),
            f"{feature_name}_trend": float(arr[-1] - arr[0])  # 🔥 motion direction
        }

    # ----------- 🔥 PHASE DETECTION ----------- #
    def get_movement_phase(self, feature_name):
        """
        Detect movement phase (VERY IMPORTANT for reps)
        """
        vel = self.velocities.get(feature_name, 0)

        if vel < -5:
            return "DOWN"
        elif vel > 5:
            return "UP"
        else:
            return "STATIC"

    def get_velocity(self, feature_name):
        return self.velocities.get(feature_name, 0.0)

    def get_acceleration(self, feature_name):
        return self.accelerations.get(feature_name, 0.0)