import os

PROJECT_NAME = "AI_Fitness_Tracker"

# Folder structure
folders = [
    "backend",
    "backend/__pycache__",
    "src",
    "src/camera",
    "src/coach",
    "src/controller",
    "src/exercises",
    "src/pose",
    "src/utils",
    "src/voice",
]

# Files to create (empty files)
files = [
    "app.py",
    "requirements.txt",
    ".gitignore",
    "README.md",
    ".env",

    # Backend
    "backend/__init__.py",
    "backend/main.py",
    "backend/auth.py",
    "backend/database.py",
    "backend/dependencies.py",
    "backend/models.py",
    "backend/schemas.py",
    "backend/profile.py",
    "backend/workout.py",
    "backend/utils.py",

    # Src main
    "src/main.py",

    # Camera
    "src/camera/webcam.py",

    # Coach
    "src/coach/fitness_tracker.py",
    "src/coach/llm_coach.py",

    # Controller
    "src/controller/session_controller.py",

    # Exercises
    "src/exercises/squat.py",
    "src/exercises/pushup.py",
    "src/exercises/plank.py",
    "src/exercises/chair_pose.py",
    "src/exercises/tree_pose.py",
    "src/exercises/high_knees.py",

    # Pose
    "src/pose/pose_detector.py",
    "src/pose/angle_calculator.py",

    # Utils
    "src/utils/helpers.py",

    # Voice
    "src/voice/speech_to_text.py",
    "src/voice/text_to_speech.py",
    "src/voice/voice_loop.py",
]

def create_structure():
    # Create root folder
    os.makedirs(PROJECT_NAME, exist_ok=True)

    # Create folders
    for folder in folders:
        os.makedirs(os.path.join(PROJECT_NAME, folder), exist_ok=True)

    # Create files
    for file in files:
        path = os.path.join(PROJECT_NAME, file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "w").close()

    print("✅ AI Fitness Tracker project structure created successfully!")

if __name__ == "__main__":
    create_structure()
