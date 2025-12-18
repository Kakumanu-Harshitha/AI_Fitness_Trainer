from gtts import gTTS
import os
import time
import uuid
from playsound3 import playsound

def speak(text):
    try:
        filename = f"tts_{uuid.uuid4().hex}.mp3"

        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        playsound(filename)

        time.sleep(0.1)
        os.remove(filename)

    except Exception as e:
        print("TTS error:", e)
