import json
import queue

import pyttsx3
import sounddevice as sd
import vosk

# --- Speech-to-Text (Vosk) ---
MODEL_PATH = "vosk-model-small-hu-0.22"  # magyar modell letöltése szükséges: https://alphacephei.com/vosk/models

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def recognize_from_mic():
    model = vosk.Model(MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, 16000)
    with sd.RawInputStream(
        samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback
    ):
        print("Beszélj a mikrofonba (Ctrl+C a kilépéshez)...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("Felismert szöveg:", result.get("text", ""))
                return result.get("text", "")


# --- Text-to-Speech (pyttsx3) ---
def speak(text):
    engine = pyttsx3.init()
    # Magyar hang kiválasztása, ha elérhető
    for voice in engine.getProperty("voices"):
        if "hu" in voice.languages or "Hungarian" in voice.name:
            engine.setProperty("voice", voice.id)
            break
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    try:
        text = recognize_from_mic()
        if text:
            print("Felolvasom:", text)
            speak(text)
    except KeyboardInterrupt:
        print("Kilépés.")
    except Exception as e:
        print("Hiba:", e)
