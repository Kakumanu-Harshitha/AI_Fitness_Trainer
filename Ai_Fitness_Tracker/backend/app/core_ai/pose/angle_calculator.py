import numpy as np
import math


def calculate_angle(a, b, c):
    """
    Calculates angle at point b
    a, b, c are (x, y) tuples
    """

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    # Vectors
    ba = a - b
    bc = c - b

    # Cosine angle formula
    cosine_angle = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    angle = np.degrees(np.arccos(cosine_angle))

    return angle
