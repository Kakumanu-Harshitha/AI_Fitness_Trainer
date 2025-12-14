from voice.speech_to_text import listen
from coach.llm_coach import ask_llm
from voice.text_to_speech import speak
import time

def voice_loop(tracker, session):
    print("🎤 Voice loop active")

    while session.running:
        user_text = listen()
        if not user_text or user_text.strip() == "":
            time.sleep(0.5)  
        if not user_text:
            continue
        

        print("🗣️ User:", user_text)

        response = ask_llm(
            fitness_summary=tracker.summary(),
            user_message=user_text
        )

        print("🤖 AI:", response)
        speak(response)
        time.sleep(1.0)
