import os

PROJECT_NAME = "ai_fitness_trainer"

folders = [
    "config",
    "camera",
    "pose",
    "exercises",
    "counter",
    "voice",
    "session",
    "utils"
]

files = {
    "main.py": "",
    "requirements.txt": "",
    "config/settings.py": "",
    "camera/webcam.py": "",
    "pose/pose_detector.py": "",
    "pose/angle_calculator.py": "",
    "exercises/exercise_base.py": "",
    "exercises/squat.py": "",
    "counter/rep_counter.py": "",
    "voice/speech_to_text.py": "",
    "voice/text_to_speech.py": "",
    "voice/voice_commands.py": "",
    "session/workout_session.py": "",
    "utils/helpers.py": "",
    "README.md": ""
}


def create_project():
    if not os.path.exists(PROJECT_NAME):
        os.mkdir(PROJECT_NAME)

    for folder in folders:
        os.makedirs(os.path.join(PROJECT_NAME, folder), exist_ok=True)

    for file_path, content in files.items():
        full_path = os.path.join(PROJECT_NAME, file_path)
        with open(full_path, "w") as f:
            f.write(content)

    print("✅ Project structure created successfully!")


if __name__ == "__main__":
    create_project()
