from __future__ import annotations

from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, HTTPException

from jarvis.agent.runtime import build_runtime
from jarvis.api.schemas import CommandRequest, CommandResponse, ConfirmationResponse
from jarvis.core.models import ActionStatus

runtime = build_runtime()
app = FastAPI(title="JARVIS Local Desktop Assistant", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": runtime.settings.permission_mode, "dry_run": str(runtime.settings.dry_run)}


@app.post("/v1/command", response_model=CommandResponse)
def command(request: CommandRequest) -> CommandResponse:
    plan, results = runtime.handle_text(request.text)
    return CommandResponse(
        command=plan.original_text,
        plan=[asdict(step) for step in plan.steps],
        results=[asdict(result) for result in results],
    )


@app.post("/v1/confirm/{confirmation_id}", response_model=ConfirmationResponse)
def confirm(confirmation_id: str) -> ConfirmationResponse:
    pending = runtime.safety.approve(confirmation_id)
    if pending is None:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    result = runtime.executor.execute_confirmed(pending.command, pending.call)
    return ConfirmationResponse(ok=result.ok, message=result.message, result=asdict(result))


@app.post("/v1/deny/{confirmation_id}", response_model=ConfirmationResponse)
def deny(confirmation_id: str) -> ConfirmationResponse:
    if not runtime.safety.deny(confirmation_id):
        raise HTTPException(status_code=404, detail="Confirmation not found")
    return ConfirmationResponse(ok=True, message="Denied", result={"status": ActionStatus.BLOCKED.value})


@app.get("/v1/apps")
def apps() -> list[dict[str, str]]:
    return runtime.apps.list()


@app.get("/v1/audit")
def audit(limit: int = 100):
    return runtime.audit.recent(limit)


@app.get("/v1/memory/conversation")
def conversation(limit: int = 30):
    return runtime.memory.recent_turns(limit)


def main() -> None:
    uvicorn.run(app, host=runtime.settings.host, port=runtime.settings.port)


if __name__ == "__main__":
    main()
