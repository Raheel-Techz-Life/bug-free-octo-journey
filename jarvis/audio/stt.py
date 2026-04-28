from __future__ import annotations

from pathlib import Path

from jarvis.core.config import Settings


class SpeechToText:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None

    def transcribe_file(self, path: Path) -> str:
        if self.settings.stt_backend == "console":
            return input("You said: ").strip()
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self.settings.stt_model, device="cpu", compute_type="int8")
        segments, _info = self._model.transcribe(str(path), vad_filter=True, beam_size=1)
        return " ".join(segment.text.strip() for segment in segments).strip()
