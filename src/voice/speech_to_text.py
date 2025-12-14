import speech_recognition as sr

recognizer = sr.Recognizer()

recognizer.pause_threshold = 2.0            
recognizer.non_speaking_duration = 1.0      # allow small pauses while speaking

def listen():
    try:
        with sr.Microphone() as source:
            print("🎙️ Speak now...")

            # Adjust once for background noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        return text.lower()

    except sr.UnknownValueError:
        return ""

    except Exception as e:
        print("Mic error:", e)
        return ""
