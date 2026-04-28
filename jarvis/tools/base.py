from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from jarvis.core.models import SafetyLevel, ToolResult


class Tool(ABC):
    name: str
    description: str
    default_safety: SafetyLevel = SafetyLevel.SAFE

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError
