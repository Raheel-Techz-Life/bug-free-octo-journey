from __future__ import annotations

import logging

from jarvis.core.audit import AuditLog
from jarvis.core.config import Settings
from jarvis.core.models import ActionStatus, Plan, ToolCall, ToolResult
from jarvis.core.safety import SafetyManager
from jarvis.memory.store import MemoryStore
from jarvis.tools.base import Tool
from jarvis.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentTool(Tool):
    name = "agent"
    description = "Agent meta operations such as clarification."

    def run(self, **kwargs: object) -> ToolResult:
        operation = kwargs.get("operation")
        if operation == "clarify":
            return ToolResult(
                False,
                "I need a more specific command. Try naming the app, file path, or action.",
                status=ActionStatus.FAILED,
            )
        return ToolResult(False, f"Unknown agent operation: {operation}", status=ActionStatus.FAILED)


class AgentExecutor:
    def __init__(
        self,
        *,
        settings: Settings,
        tools: ToolRegistry,
        safety: SafetyManager,
        audit: AuditLog,
        memory: MemoryStore,
    ) -> None:
        self.settings = settings
        self.tools = tools
        self.safety = safety
        self.audit = audit
        self.memory = memory

    def execute(self, plan: Plan) -> list[ToolResult]:
        self.memory.add_turn("user", plan.original_text)
        results: list[ToolResult] = []
        for call in plan.steps:
            result = self._execute_call(plan.original_text, call)
            results.append(result)
            if not result.ok and result.status in {ActionStatus.CONFIRMATION_REQUIRED, ActionStatus.BLOCKED}:
                break
        assistant_text = " ".join(result.message for result in results) or "No action was taken."
        self.memory.add_turn("assistant", assistant_text)
        return results

    def execute_confirmed(self, command: str, call: ToolCall) -> ToolResult:
        return self._run_tool(command, call)

    def _execute_call(self, command: str, call: ToolCall) -> ToolResult:
        gated = self.safety.gate(command, call)
        if gated is not None:
            self._audit(command, call, gated)
            return gated
        if self.settings.dry_run and call.safety.value != "safe":
            result = ToolResult(True, f"Dry run: would run {call.tool}", {"args": call.args})
            self._audit(command, call, result)
            return result
        return self._run_tool(command, call)

    def _run_tool(self, command: str, call: ToolCall) -> ToolResult:
        try:
            result = self.tools.get(call.tool).run(**call.args)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            logger.exception("Tool failed: %s", call.tool)
            result = ToolResult(False, str(exc), status=ActionStatus.FAILED)
        self._audit(command, call, result)
        return result

    def _audit(self, command: str, call: ToolCall, result: ToolResult) -> None:
        self.audit.write(
            command=command,
            tool=call.tool,
            safety=call.safety.value,
            status=result.status.value,
            args=call.args,
            result={"ok": result.ok, "message": result.message, "data": result.data},
        )
