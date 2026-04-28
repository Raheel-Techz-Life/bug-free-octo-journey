from __future__ import annotations

from collections import deque
from typing import Any

import pyperclip

from jarvis.core.config import Settings
from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool


class ClipboardManager:
    def __init__(self, settings: Settings, max_items: int = 25) -> None:
        self.settings = settings
        self.history: deque[str] = deque(maxlen=max_items)

    def get(self) -> ToolResult:
        value = pyperclip.paste()
        if value and (not self.history or self.history[-1] != value):
            self.history.append(value)
        return ToolResult(True, "Read clipboard", {"text": value})

    def set(self, text: str) -> ToolResult:
        if not self.settings.dry_run:
            pyperclip.copy(text)
        self.history.append(text)
        return ToolResult(True, "Updated clipboard", {"chars": len(text)})

    def list_history(self) -> ToolResult:
        return ToolResult(True, "Clipboard history", {"items": list(self.history)})


class ClipboardTool(Tool):
    name = "clipboard"
    description = "Read, write, and list local clipboard history."
    default_safety = SafetyLevel.SENSITIVE

    def __init__(self, manager: ClipboardManager) -> None:
        self.manager = manager

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.pop("operation")
        return getattr(self.manager, operation)(**kwargs)
