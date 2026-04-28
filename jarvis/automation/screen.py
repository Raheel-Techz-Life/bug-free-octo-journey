from __future__ import annotations

from datetime import datetime
from typing import Any

import pyautogui

from jarvis.core.config import Settings
from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool


class ScreenAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def screenshot(self) -> ToolResult:
        path = self.settings.data_dir / "screenshots" / f"screen-{datetime.now():%Y%m%d-%H%M%S}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot()
        image.save(path)
        return ToolResult(True, f"Saved screenshot {path}", {"path": str(path)})

    def ocr(self) -> ToolResult:
        if not self.settings.enable_ocr:
            return ToolResult(False, "OCR is disabled")
        import pytesseract

        image = pyautogui.screenshot()
        text = pytesseract.image_to_string(image)
        return ToolResult(True, "Read screen text", {"text": text})


class ScreenTool(Tool):
    name = "screen"
    description = "Take screenshots and run OCR on the current screen."
    default_safety = SafetyLevel.SAFE

    def __init__(self, analyzer: ScreenAnalyzer) -> None:
        self.analyzer = analyzer

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.pop("operation")
        return getattr(self.analyzer, operation)(**kwargs)
