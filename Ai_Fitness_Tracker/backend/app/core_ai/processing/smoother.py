import math
import time

# ---------- One Euro Filter ----------
class OneEuroFilter:
    def __init__(self, min_cutoff=0.1, beta=10.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exp_smooth(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def filter(self, t, x):
        if self.t_prev is None:
            self.t_prev = t
            self.x_prev = x
            return x

        t_e = max(t - self.t_prev, 1e-6)

        dx = (x - self.x_prev) / t_e
        a_d = self.smoothing_factor(t_e, self.d_cutoff)
        dx_hat = self.exp_smooth(a_d, dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self.smoothing_factor(t_e, cutoff)
        x_hat = self.exp_smooth(a, x, self.x_prev)

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat


# ---------- Smoothed Landmark ----------
class SmoothedLandmark:
    __slots__ = ['x', 'y', 'z', 'visibility']  # 🔥 memory optimization

    def __init__(self, x, y, z, visibility):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


# ---------- Pose Smoother ----------
class PoseSmoother:
    def __init__(self, num_landmarks=33, min_cutoff=0.1, beta=10.0, d_cutoff=1.0):
        self.num_landmarks = num_landmarks
        self.filters = {}

        self.config = {
            'min_cutoff': min_cutoff,
            'beta': beta,
            'd_cutoff': d_cutoff
        }

        self.prev_time = None

    def smooth(self, landmarks):
        if not landmarks:
            return []

        # 🔥 Stable time delta (better than time.time jitter)
        current_time = time.perf_counter()

        smoothed = []

        for i, lm in enumerate(landmarks):

            # Skip low confidence points
            if lm.visibility < 0.5:
                smoothed.append(lm)
                continue

            # Create filters once
            if i not in self.filters:
                self.filters[i] = {
                    'x': OneEuroFilter(**self.config),
                    'y': OneEuroFilter(**self.config),
                    'z': OneEuroFilter(**self.config),
                    'v': OneEuroFilter(**self.config)
                }

            f = self.filters[i]

            s_x = f['x'].filter(current_time, lm.x)
            s_y = f['y'].filter(current_time, lm.y)
            s_z = f['z'].filter(current_time, lm.z)
            s_v = f['v'].filter(current_time, lm.visibility)

            smoothed.append(SmoothedLandmark(s_x, s_y, s_z, s_v))

        return smoothed