from __future__ import annotations

from typing import Protocol

from jarvis.tools.registry import ToolRegistry


class JarvisPlugin(Protocol):
    name: str

    def register(self, registry: ToolRegistry) -> None:
        """Register one or more tools."""
