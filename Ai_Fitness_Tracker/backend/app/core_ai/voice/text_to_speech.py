import os
import time
import uuid

try:
    from gtts import gTTS
    from playsound3 import playsound
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

def speak(text):
    if not HAS_TTS:
        print(f"🔊 TTS would say: {text} (Hardware not supported in this environment)")
        return

    try:
        filename = f"tts_{uuid.uuid4().hex}.mp3"

        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        playsound(filename)

        time.sleep(0.1)
        os.remove(filename)

    except Exception as e:
        print("TTS error (likely no audio device):", e)
