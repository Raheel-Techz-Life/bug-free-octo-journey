from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from jarvis.core.config import Settings
from jarvis.core.models import SafetyLevel, ToolCall, ToolResult, ActionStatus


BLOCKED_PATH_PARTS = {
    "windows",
    "system32",
    "program files",
    "program files (x86)",
    ".ssh",
    ".gnupg",
}


@dataclass(slots=True)
class PendingConfirmation:
    id: str
    command: str
    call: ToolCall


class SafetyManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.pending: dict[str, PendingConfirmation] = {}

    def classify_path(self, path: Path, destructive: bool = False) -> SafetyLevel:
        resolved = path.expanduser().resolve()
        parts = {part.lower() for part in resolved.parts}
        if parts & BLOCKED_PATH_PARTS:
            return SafetyLevel.DANGEROUS
        allowed = any(self._is_relative_to(resolved, root.expanduser().resolve()) for root in self.settings.workspace_roots)
        if not allowed:
            return SafetyLevel.DANGEROUS if destructive else SafetyLevel.SENSITIVE
        return SafetyLevel.SENSITIVE if destructive else SafetyLevel.SAFE

    def gate(self, command: str, call: ToolCall) -> ToolResult | None:
        if call.safety == SafetyLevel.DANGEROUS or self.settings.permission_mode == "locked":
            return ToolResult(
                ok=False,
                message=f"Blocked dangerous action: {call.tool}",
                status=ActionStatus.BLOCKED,
            )
        if self.settings.dry_run:
            return None
        if self.settings.permission_mode == "confirm" and call.safety == SafetyLevel.SENSITIVE:
            confirmation_id = str(uuid4())
            self.pending[confirmation_id] = PendingConfirmation(confirmation_id, command, call)
            return ToolResult(
                ok=False,
                message=f"Confirmation required for {call.tool}",
                status=ActionStatus.CONFIRMATION_REQUIRED,
                confirmation_id=confirmation_id,
            )
        return None

    def approve(self, confirmation_id: str) -> PendingConfirmation | None:
        return self.pending.pop(confirmation_id, None)

    def deny(self, confirmation_id: str) -> bool:
        return self.pending.pop(confirmation_id, None) is not None

    @staticmethod
    def _is_relative_to(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False
