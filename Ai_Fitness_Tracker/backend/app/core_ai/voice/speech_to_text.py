try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

def listen(timeout=1.5, phrase_time_limit=5.0):
    if not HAS_SR:
        print("🎙️ Speech Recognition not installed/supported in this environment.")
        return ""

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0
    recognizer.non_speaking_duration = 1.0

    try:
        with sr.Microphone() as source:
            print("🎙️ Speak now...")
            # Note: adjust_for_ambient_noise can be slow, keeping it simple for now
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        text = recognizer.recognize_google(audio)
        return text.lower()

    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""

    except Exception as e:
        print("Mic error (likely no hardware):", e)
        return ""
