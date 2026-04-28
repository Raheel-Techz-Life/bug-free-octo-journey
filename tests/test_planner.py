from jarvis.agent.planner import IntentPlanner
from jarvis.core.config import Settings
from jarvis.core.safety import SafetyManager


def planner() -> IntentPlanner:
    return IntentPlanner(SafetyManager(Settings(dry_run=True)))


def test_open_app_plan() -> None:
    plan = planner().plan("open notepad")
    assert plan.steps[0].tool == "desktop"
    assert plan.steps[0].args["operation"] == "open_app"


def test_delete_is_not_safe() -> None:
    plan = planner().plan("delete desktop/temp.txt")
    assert plan.steps[0].tool == "filesystem"
    assert plan.steps[0].safety.value in {"sensitive", "dangerous"}
