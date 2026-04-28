from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class SafetyLevel(str, Enum):
    SAFE = "safe"
    SENSITIVE = "sensitive"
    DANGEROUS = "dangerous"


class ActionStatus(str, Enum):
    PLANNED = "planned"
    CONFIRMATION_REQUIRED = "confirmation_required"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(slots=True)
class ToolCall:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    safety: SafetyLevel = SafetyLevel.SAFE
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ToolResult:
    ok: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    status: ActionStatus = ActionStatus.EXECUTED
    confirmation_id: str | None = None


@dataclass(slots=True)
class Plan:
    original_text: str
    steps: list[ToolCall]
    summary: str
