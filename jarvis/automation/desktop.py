from __future__ import annotations

import subprocess
from typing import Any

import pyautogui

try:
    import pygetwindow as gw
except Exception:  # pragma: no cover - platform dependent
    gw = None

from jarvis.apps.registry import AppRegistry
from jarvis.core.config import Settings
from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool


class DesktopController:
    def __init__(self, settings: Settings, apps: AppRegistry) -> None:
        self.settings = settings
        self.apps = apps
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05

    def open_app(self, name: str) -> ToolResult:
        app = self.apps.find(name)
        if app is None:
            return ToolResult(False, f"Could not find installed app matching {name!r}")
        if self.settings.dry_run:
            return ToolResult(True, f"Dry run: would open {app.name}", {"command": app.command})
        subprocess.Popen([app.command], shell=app.command.lower().endswith(".lnk"))
        return ToolResult(True, f"Opened {app.name}", {"command": app.command})

    def close_window(self, title: str | None = None) -> ToolResult:
        if gw is None:
            return ToolResult(False, "Window control is unavailable on this platform")
        windows = gw.getWindowsWithTitle(title) if title else [gw.getActiveWindow()]
        windows = [window for window in windows if window]
        if not windows:
            return ToolResult(False, "No matching window found")
        if self.settings.dry_run:
            return ToolResult(True, f"Dry run: would close {windows[0].title}")
        windows[0].close()
        return ToolResult(True, f"Closed {windows[0].title}")

    def switch_window(self, title: str) -> ToolResult:
        if gw is None:
            return ToolResult(False, "Window control is unavailable on this platform")
        matches = gw.getWindowsWithTitle(title)
        if not matches:
            return ToolResult(False, f"No window found with title containing {title!r}")
        if not self.settings.dry_run:
            matches[0].activate()
        return ToolResult(True, f"Switched to {matches[0].title}")

    def hotkey(self, keys: list[str]) -> ToolResult:
        if not self.settings.dry_run:
            pyautogui.hotkey(*keys)
        return ToolResult(True, f"Pressed {'+'.join(keys)}")

    def type_text(self, text: str) -> ToolResult:
        if not self.settings.dry_run:
            pyautogui.write(text, interval=0.01)
        return ToolResult(True, f"Typed {len(text)} characters")


class DesktopTool(Tool):
    name = "desktop"
    description = "Open apps, switch windows, close windows, press hotkeys, and type text."
    default_safety = SafetyLevel.SENSITIVE

    def __init__(self, controller: DesktopController) -> None:
        self.controller = controller

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.pop("operation")
        method = getattr(self.controller, operation)
        return method(**kwargs)
