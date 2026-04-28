from __future__ import annotations

from jarvis.core.config import Settings


class WakeWordDetector:
    """Lightweight wake-word gate.

    Production deployments should swap this for Porcupine, openWakeWord, or a tiny VAD +
    keyword model. The console backend keeps the architecture testable without audio hardware.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def wait(self) -> str:
        prompt = f"Say '{self.settings.wake_word}' command (or type quit): "
        text = input(prompt).strip()
        return text

    def strip_wake_word(self, text: str) -> str | None:
        lowered = text.lower().strip()
        wake = self.settings.wake_word.lower()
        if lowered == "quit":
            return None
        if lowered.startswith(wake):
            return text[len(self.settings.wake_word) :].strip(" ,")
        return text
