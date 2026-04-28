from jarvis.core.models import SafetyLevel, ToolResult
from jarvis.tools.base import Tool


class ExampleTool(Tool):
    name = "example"
    description = "Example plugin tool."
    default_safety = SafetyLevel.SAFE

    def run(self, **kwargs):
        return ToolResult(True, "Example plugin executed", {"kwargs": kwargs})


class ExamplePlugin:
    name = "example"

    def register(self, registry):
        registry.register(ExampleTool())


def create_plugin():
    return ExamplePlugin()
