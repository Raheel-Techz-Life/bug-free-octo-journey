from __future__ import annotations

from typing import Any
import webbrowser

from jarvis.core.config import Settings
from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool


class BrowserController:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def open_url(self, url: str) -> ToolResult:
        if not self.settings.enable_browser:
            return ToolResult(False, "Browser automation is disabled")
        if self.settings.dry_run:
            return ToolResult(True, f"Dry run: would open {url}")
        webbrowser.open(url)
        return ToolResult(True, f"Opened {url}")

    def search_web(self, query: str) -> ToolResult:
        from urllib.parse import quote_plus

        return self.open_url(f"https://www.google.com/search?q={quote_plus(query)}")


class BrowserTool(Tool):
    name = "browser"
    description = "Open URLs and perform browser searches."
    default_safety = SafetyLevel.SENSITIVE

    def __init__(self, controller: BrowserController) -> None:
        self.controller = controller

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.pop("operation")
        return getattr(self.controller, operation)(**kwargs)
