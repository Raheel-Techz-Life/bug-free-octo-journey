from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

from jarvis.core.config import Settings
from jarvis.core.models import ActionStatus, SafetyLevel, ToolResult
from jarvis.core.safety import SafetyManager
from jarvis.tools.base import Tool


class FileSystemAgent:
    def __init__(self, settings: Settings, safety: SafetyManager) -> None:
        self.settings = settings
        self.safety = safety

    def resolve_user_path(self, raw: str) -> Path:
        lowered = raw.strip().strip('"')
        home = Path.home()
        replacements = {
            "desktop": home / "Desktop",
            "documents": home / "Documents",
            "downloads": home / "Downloads",
        }
        for key, root in replacements.items():
            if lowered.lower() == key:
                return root
            prefix = f"{key}/"
            if lowered.lower().startswith(prefix):
                return root / lowered[len(prefix) :]
        return Path(lowered).expanduser()

    def read_text(self, path: str, max_chars: int = 8000) -> ToolResult:
        target = self.resolve_user_path(path)
        level = self.safety.classify_path(target)
        if level == SafetyLevel.DANGEROUS:
            return ToolResult(False, f"Blocked read outside allowed roots: {target}", status=ActionStatus.BLOCKED)
        if not target.exists() or not target.is_file():
            return ToolResult(False, f"File not found: {target}", status=ActionStatus.FAILED)
        text = target.read_text(encoding="utf-8", errors="replace")[:max_chars]
        return ToolResult(True, f"Read {target}", {"path": str(target), "content": text})

    def write_text(self, path: str, content: str, append: bool = False) -> ToolResult:
        target = self.resolve_user_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with target.open(mode, encoding="utf-8") as handle:
            handle.write(content)
        return ToolResult(True, f"Wrote {target}", {"path": str(target), "bytes": len(content.encode())})

    def mkdir(self, path: str) -> ToolResult:
        target = self.resolve_user_path(path)
        target.mkdir(parents=True, exist_ok=True)
        return ToolResult(True, f"Created folder {target}", {"path": str(target)})

    def delete(self, path: str) -> ToolResult:
        target = self.resolve_user_path(path)
        if not target.exists():
            return ToolResult(False, f"Path not found: {target}", status=ActionStatus.FAILED)
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return ToolResult(True, f"Deleted {target}", {"path": str(target)})

    def move(self, source: str, destination: str) -> ToolResult:
        src = self.resolve_user_path(source)
        dst = self.resolve_user_path(destination)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return ToolResult(True, f"Moved {src} to {dst}", {"source": str(src), "destination": str(dst)})

    def copy(self, source: str, destination: str) -> ToolResult:
        src = self.resolve_user_path(source)
        dst = self.resolve_user_path(destination)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        return ToolResult(True, f"Copied {src} to {dst}", {"source": str(src), "destination": str(dst)})

    def search(self, query: str, root: str | None = None, limit: int = 20) -> ToolResult:
        roots = [self.resolve_user_path(root)] if root else self.settings.workspace_roots
        matches: list[dict[str, Any]] = []
        for base in roots:
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if len(matches) >= limit:
                    break
                if not path.is_file():
                    continue
                score = fuzz.partial_ratio(query.lower(), path.name.lower())
                if score < 65:
                    try:
                        if path.stat().st_size <= 1_000_000:
                            sample = path.read_text(encoding="utf-8", errors="ignore")[:4000]
                            score = max(score, fuzz.partial_ratio(query.lower(), sample.lower()))
                    except OSError:
                        pass
                if score >= 65:
                    matches.append({"path": str(path), "score": score})
        matches.sort(key=lambda item: item["score"], reverse=True)
        return ToolResult(True, f"Found {len(matches)} matches", {"matches": matches[:limit]})


class FileTool(Tool):
    name = "filesystem"
    description = "Create, read, update, delete, move, copy, and search files."
    default_safety = SafetyLevel.SENSITIVE

    def __init__(self, agent: FileSystemAgent) -> None:
        self.agent = agent

    def run(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.pop("operation")
        method = getattr(self.agent, operation)
        return method(**kwargs)
