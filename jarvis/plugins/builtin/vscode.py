from __future__ import annotations

import subprocess
from typing import Any

from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool
from jarvis.tools.registry import ToolRegistry


class VSCodeTool(Tool):
    name = "vscode"
    description = "Open files or folders in Visual Studio Code."
    default_safety = SafetyLevel.SENSITIVE

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.get("operation", "open")
        target = str(kwargs.get("path", "."))
        if operation != "open":
            return ToolResult(False, f"Unknown VS Code operation: {operation}")
        subprocess.Popen(["code", target])
        return ToolResult(True, f"Opened {target} in VS Code")


class VSCodePlugin:
    name = "vscode"

    def register(self, registry: ToolRegistry) -> None:
        registry.register(VSCodeTool())
