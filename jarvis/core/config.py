from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from platformdirs import user_data_dir
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PermissionMode = Literal["auto", "confirm", "locked"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="JARVIS_", extra="ignore")

    app_name: str = "JARVIS"
    env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8765
    dry_run: bool = True
    permission_mode: PermissionMode = "confirm"
    data_dir: Path = Field(default_factory=lambda: Path(user_data_dir("JARVIS", "LocalAI")))
    workspace_roots: list[Path] = Field(default_factory=list)
    log_level: str = "INFO"

    wake_word: str = "jarvis"
    stt_backend: Literal["console", "faster_whisper"] = "console"
    stt_model: str = "base.en"
    tts_backend: Literal["console", "piper", "pyttsx3"] = "console"
    piper_bin: str | None = None
    piper_model: str | None = None

    local_llm_url: str | None = None
    local_llm_model: str | None = None
    plugins_dir: Path | None = None
    enable_browser: bool = True
    enable_ocr: bool = True

    @field_validator("workspace_roots", mode="before")
    @classmethod
    def parse_roots(cls, value: object) -> list[Path]:
        if value in (None, ""):
            home = Path.home()
            return [home / "Desktop", home / "Documents", home / "Downloads"]
        if isinstance(value, str):
            return [Path(part.strip()).expanduser() for part in value.split(",") if part.strip()]
        return value  # type: ignore[return-value]

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "plugins").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
