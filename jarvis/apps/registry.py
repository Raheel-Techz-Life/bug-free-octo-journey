from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from rapidfuzz import process


@dataclass(frozen=True, slots=True)
class AppEntry:
    name: str
    command: str
    source: str


class AppRegistry:
    COMMON_ALIASES = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "vs code": "code",
        "visual studio code": "code",
        "notepad": "notepad",
        "calculator": "calc",
        "terminal": "wt",
        "powershell": "powershell",
        "explorer": "explorer",
        "file explorer": "explorer",
    }

    def __init__(self) -> None:
        self._apps: dict[str, AppEntry] = {}
        self.refresh()

    def refresh(self) -> None:
        self._apps.clear()
        for name, command in self.COMMON_ALIASES.items():
            resolved = shutil.which(command) or command
            self._apps[name] = AppEntry(name=name, command=resolved, source="alias")
        self._scan_start_menu()

    def _scan_start_menu(self) -> None:
        roots = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
        ]
        for root in roots:
            if not root.exists():
                continue
            for shortcut in root.rglob("*.lnk"):
                name = shortcut.stem.lower()
                self._apps.setdefault(name, AppEntry(name=shortcut.stem, command=str(shortcut), source="start-menu"))

    def find(self, natural_name: str) -> AppEntry | None:
        if not self._apps:
            self.refresh()
        key = natural_name.strip().lower()
        if key in self._apps:
            return self._apps[key]
        match = process.extractOne(key, self._apps.keys(), score_cutoff=70)
        return self._apps[match[0]] if match else None

    def list(self) -> list[dict[str, str]]:
        return [entry.__dict__ for entry in sorted(self._apps.values(), key=lambda app: app.name.lower())]
