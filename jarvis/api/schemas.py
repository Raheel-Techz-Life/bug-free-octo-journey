from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    text: str = Field(min_length=1)


class CommandResponse(BaseModel):
    command: str
    plan: list[dict[str, Any]]
    results: list[dict[str, Any]]


class ConfirmationResponse(BaseModel):
    ok: bool
    message: str
    result: dict[str, Any] | None = None
