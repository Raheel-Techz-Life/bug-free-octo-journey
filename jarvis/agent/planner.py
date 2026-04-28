from __future__ import annotations

import re
from pathlib import Path

from jarvis.core.models import Plan, SafetyLevel, ToolCall
from jarvis.core.safety import SafetyManager


class IntentPlanner:
    """Deterministic command router with room for an LLM planner behind the same interface."""

    def __init__(self, safety: SafetyManager) -> None:
        self.safety = safety

    def plan(self, text: str) -> Plan:
        normalized = text.strip()
        lower = normalized.lower()
        steps: list[ToolCall] = []

        if match := re.match(r"^(open|launch|start)\s+(.+)$", lower):
            target = normalized[match.start(2) :].strip()
            if target.startswith("http://") or target.startswith("https://"):
                steps.append(ToolCall("browser", {"operation": "open_url", "url": target}, SafetyLevel.SENSITIVE))
            else:
                steps.append(ToolCall("desktop", {"operation": "open_app", "name": target}, SafetyLevel.SENSITIVE))

        elif match := re.match(r"^(close)\s+(.+)$", lower):
            title = normalized[match.start(2) :].strip()
            steps.append(ToolCall("desktop", {"operation": "close_window", "title": title}, SafetyLevel.SENSITIVE))

        elif match := re.match(r"^(switch to|focus)\s+(.+)$", lower):
            title = normalized[match.start(2) :].strip()
            steps.append(ToolCall("desktop", {"operation": "switch_window", "title": title}, SafetyLevel.SENSITIVE))

        elif lower.startswith("search web for "):
            query = normalized[len("search web for ") :].strip()
            steps.append(ToolCall("browser", {"operation": "search_web", "query": query}, SafetyLevel.SENSITIVE))

        elif lower.startswith("take a screenshot") or lower == "screenshot":
            steps.append(ToolCall("screen", {"operation": "screenshot"}, SafetyLevel.SAFE))

        elif "what text is visible" in lower or lower.startswith("read the screen"):
            steps.append(ToolCall("screen", {"operation": "ocr"}, SafetyLevel.SAFE))

        elif lower.startswith("copy to clipboard "):
            text_to_copy = normalized[len("copy to clipboard ") :]
            steps.append(ToolCall("clipboard", {"operation": "set", "text": text_to_copy}, SafetyLevel.SENSITIVE))

        elif lower in {"read clipboard", "what is on my clipboard"}:
            steps.append(ToolCall("clipboard", {"operation": "get"}, SafetyLevel.SAFE))

        elif match := re.match(r"^create (a )?folder (called|named)?\s*(.+)$", lower):
            path = self._clean_path(normalized[match.start(3) :])
            steps.append(ToolCall("filesystem", {"operation": "mkdir", "path": path}, SafetyLevel.SENSITIVE))

        elif match := re.match(r"^create (a )?file (called|named)?\s*(.+?)( with (.+))?$", lower):
            path = self._clean_path(normalized[match.start(3) : match.start(4) if match.group(4) else len(normalized)])
            content = match.group(5) or ""
            steps.append(
                ToolCall(
                    "filesystem",
                    {"operation": "write_text", "path": path, "content": content, "append": False},
                    SafetyLevel.SENSITIVE,
                )
            )

        elif lower.startswith("read file "):
            path = self._clean_path(normalized[len("read file ") :])
            steps.append(ToolCall("filesystem", {"operation": "read_text", "path": path}, SafetyLevel.SAFE))

        elif lower.startswith("delete "):
            path = self._clean_path(normalized[len("delete ") :])
            level = self.safety.classify_path(Path(path), destructive=True)
            steps.append(ToolCall("filesystem", {"operation": "delete", "path": path}, level))

        elif match := re.match(r"^(rename|move)\s+(.+?)\s+to\s+(.+)$", lower):
            source = self._clean_path(normalized[match.start(2) : match.end(2)])
            destination = self._clean_path(normalized[match.start(3) :])
            level = max(
                self.safety.classify_path(Path(source), destructive=True),
                self.safety.classify_path(Path(destination), destructive=False),
                key=lambda item: ["safe", "sensitive", "dangerous"].index(item.value),
            )
            steps.append(
                ToolCall(
                    "filesystem",
                    {"operation": "move", "source": source, "destination": destination},
                    level,
                )
            )

        elif match := re.match(r"^copy\s+(.+?)\s+to\s+(.+)$", lower):
            source = self._clean_path(normalized[match.start(1) : match.end(1)])
            destination = self._clean_path(normalized[match.start(2) :])
            steps.append(
                ToolCall(
                    "filesystem",
                    {"operation": "copy", "source": source, "destination": destination},
                    SafetyLevel.SENSITIVE,
                )
            )

        elif lower.startswith("search ") and " for " in lower:
            before, query = normalized.split(" for ", 1)
            root = before.replace("search", "", 1).strip() or None
            steps.append(ToolCall("filesystem", {"operation": "search", "query": query, "root": root}, SafetyLevel.SAFE))

        else:
            steps.append(ToolCall("agent", {"operation": "clarify", "text": normalized}, SafetyLevel.SAFE))

        return Plan(original_text=normalized, steps=steps, summary=f"Planned {len(steps)} step(s)")

    @staticmethod
    def _clean_path(value: str) -> str:
        cleaned = value.strip().strip(".").strip()
        prefixes = ["called ", "named ", "the file ", "the folder "]
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix) :]
        return cleaned.strip('"')
