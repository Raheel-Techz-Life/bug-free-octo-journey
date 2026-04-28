from __future__ import annotations

import subprocess
import tempfile
import wave

from jarvis.core.config import Settings


class TextToSpeech:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pyttsx3 = None

    def speak(self, text: str) -> None:
        if self.settings.tts_backend == "console":
            print(f"JARVIS: {text}")
            return
        if self.settings.tts_backend == "pyttsx3":
            self._speak_pyttsx3(text)
            return
        self._speak_piper(text)

    def _speak_pyttsx3(self, text: str) -> None:
        if self._pyttsx3 is None:
            import pyttsx3

            self._pyttsx3 = pyttsx3.init()
        self._pyttsx3.say(text)
        self._pyttsx3.runAndWait()

    def _speak_piper(self, text: str) -> None:
        if not self.settings.piper_bin or not self.settings.piper_model:
            print(f"JARVIS: {text}")
            return
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            subprocess.run(
                [self.settings.piper_bin, "--model", self.settings.piper_model, "--output_file", wav_file.name],
                input=text,
                text=True,
                check=True,
            )
            self._play_wav(wav_file.name)

    @staticmethod
    def _play_wav(path: str) -> None:
        try:
            import numpy as np
            import sounddevice as sd

            with wave.open(path, "rb") as wav:
                sample_rate = wav.getframerate()
                channels = wav.getnchannels()
                frames = wav.readframes(wav.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16)
                if channels > 1:
                    audio = audio.reshape(-1, channels)
                sd.play(audio, sample_rate)
                sd.wait()
        except Exception:
            print(f"Generated speech audio at {path}")
