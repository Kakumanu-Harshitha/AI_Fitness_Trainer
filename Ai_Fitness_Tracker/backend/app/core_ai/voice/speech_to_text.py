import speech_recognition as sr

recognizer = sr.Recognizer()

recognizer.pause_threshold = 2.0            
recognizer.non_speaking_duration = 1.0

_calibrated = False

def listen(timeout=1.5, phrase_time_limit=5.0):
    try:
        with sr.Microphone() as source:
            print("🎙️ Speak now...")
            global _calibrated
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                _calibrated = True
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        text = recognizer.recognize_google(audio)
        return text.lower()

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        return ""

    except Exception as e:
        print("Mic error:", e)
        return ""
