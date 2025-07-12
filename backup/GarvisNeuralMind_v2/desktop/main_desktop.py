import asyncio
import json
import os
import queue
import sys
import threading

import pyttsx3
import sounddevice as sd
import vosk
import websockets
from PyQt5.QtCore import QMetaObject, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

WS_URL = (
    "ws://localhost:8000/ws/community/desktop_user"
    # szükség esetén módosítsd a hostot/portot
)

STT_MODEL_PATH = "vosk-model-small-hu-0.22"  # magyar modell letöltése szükséges


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GarvisNeuralMind AI Companion")
        self.resize(900, 700)

        # Fő widget és layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Bal oldali panel: Chat UI
        left_panel = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.input_line = QLineEdit()
        self.send_btn = QPushButton("Küldés")
        self.voice_btn = QPushButton("🎤 Beszéd indítása")
        left_panel.addWidget(QLabel("Chat"))
        left_panel.addWidget(self.chat_display)
        left_panel.addWidget(self.input_line)
        left_panel.addWidget(self.send_btn)
        left_panel.addWidget(self.voice_btn)
        main_layout.addLayout(left_panel, 2)

        # Jobb oldali panel: Live2D WebView
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Live2D Avatár"))
        self.webview = QWebEngineView()
        # Betöltjük a helyi Live2D demo HTML-t
        demo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../static/voice2d-demo/index.html")
        )
        self.webview.load(QUrl.fromLocalFile(demo_path))
        right_panel.addWidget(self.webview, 1)
        main_layout.addLayout(right_panel, 3)

        # Eseménykezelők (később websocket, STT/TTS integráció)
        self.send_btn.clicked.connect(self.send_message)
        self.voice_btn.clicked.connect(self.start_voice)

        self.ws = None
        self.ws_loop = None
        self.ws_thread = threading.Thread(target=self.start_ws_loop, daemon=True)
        self.ws_thread.start()

    def start_ws_loop(self):
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        self.ws_loop.run_until_complete(self.ws_handler())

    async def ws_handler(self):
        try:
            async with websockets.connect(WS_URL) as websocket:
                self.ws = websocket
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    # Csak a chat_message típusú üzeneteket jelenítjük meg
                    if data.get("type") == "chat_message":
                        user = data.get("user_id", "AI")
                        content = data.get("content", "")
                        self.append_chat(f"<b>{user}:</b> {content}")
        except Exception as e:
            self.append_chat(f"<i>Websocket hiba: {e}</i>")

    def send_message(self):
        text = self.input_line.text().strip()
        if text:
            self.chat_display.append(f"<b>Te:</b> {text}")
            self.input_line.clear()
            # Üzenet küldése websocketen keresztül
            if self.ws and self.ws.open:
                msg = {
                    "type": "chat_message",
                    "room_id": "default",
                    "user_id": "desktop_user",
                    "content": text,
                    "message_type": "text",
                }
                asyncio.run_coroutine_threadsafe(
                    self.ws.send(json.dumps(msg)), self.ws_loop
                )

    def start_voice(self):
        self.append_chat("<i>Beszédfelismerés indítása...</i>")
        threading.Thread(target=self.stt_and_send, daemon=True).start()

    def stt_and_send(self):
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        try:
            model = vosk.Model(STT_MODEL_PATH)
            rec = vosk.KaldiRecognizer(model, 16000)
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        import json

                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            self.append_chat(f"<b>Te (STT):</b> {text}")
                            self.send_text_to_ai(text)
                        break
        except Exception as e:
            self.append_chat(f"<i>STT hiba: {e}</i>")

    def send_text_to_ai(self, text):
        if self.ws and self.ws.open:
            msg = {
                "type": "chat_message",
                "room_id": "default",
                "user_id": "desktop_user",
                "content": text,
                "message_type": "text",
            }
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps(msg)), self.ws_loop
            )

    def append_chat(self, text):
        QMetaObject.invokeMethod(self.chat_display, "append", Qt.QueuedConnection, text)
        # Ha AI válasz, olvassuk fel
        if text.startswith("<b>AI") or text.startswith("<b>assistant"):
            import re

            clean = re.sub("<[^<]+?>", "", text)
            threading.Thread(target=self.tts_speak, args=(clean,), daemon=True).start()

    def tts_speak(self, text):
        # Szájmozgás indítása a Live2D avatáron
        self.animate_avatar_mouth(True)
        engine = pyttsx3.init()
        for voice in engine.getProperty("voices"):
            if "hu" in voice.languages or "Hungarian" in voice.name:
                engine.setProperty("voice", voice.id)
                break
        engine.say(text)
        engine.runAndWait()
        # Szájmozgás leállítása
        self.animate_avatar_mouth(False)

    def animate_avatar_mouth(self, talking):
        # JS parancs a webview-nak: állítsuk a szájmozgást (pl. ParamMouthOpenY)
        if talking:
            js = (
                "if(window.model){"
                "model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', 1.0);"
                "}"
            )
        else:
            js = (
                "if(window.model){"
                "model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', 0.0);"
                "}"
            )
        self.webview.page().runJavaScript(js)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
