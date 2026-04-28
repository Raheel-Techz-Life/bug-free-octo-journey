from __future__ import annotations

from jarvis.agent.runtime import build_runtime
from jarvis.audio.tts import TextToSpeech
from jarvis.audio.wake_word import WakeWordDetector


def main() -> None:
    runtime = build_runtime()
    wake = WakeWordDetector(runtime.settings)
    tts = TextToSpeech(runtime.settings)
    tts.speak("JARVIS is online.")

    while True:
        heard = wake.wait()
        command = wake.strip_wake_word(heard)
        if command is None:
            tts.speak("Shutting down.")
            return
        if not command:
            continue
        _plan, results = runtime.handle_text(command)
        tts.speak(" ".join(result.message for result in results))


if __name__ == "__main__":
    main()
