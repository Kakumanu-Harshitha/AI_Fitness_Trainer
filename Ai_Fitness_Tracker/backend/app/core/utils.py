def calculate_calories(exercise, reps, duration):
    base = {"squat": 0.4, "pushup": 0.5, "plank": 0.3}
    return (reps + duration) * base.get(exercise, 0.3)

def calculate_posture_score(angle):
    if angle > 160: return 90
    if angle > 140: return 75
    return 60
