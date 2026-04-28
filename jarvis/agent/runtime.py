from __future__ import annotations

from dataclasses import dataclass

from jarvis.agent.executor import AgentExecutor, AgentTool
from jarvis.agent.planner import IntentPlanner
from jarvis.apps.registry import AppRegistry
from jarvis.automation.browser import BrowserController, BrowserTool
from jarvis.automation.clipboard import ClipboardManager, ClipboardTool
from jarvis.automation.desktop import DesktopController, DesktopTool
from jarvis.automation.screen import ScreenAnalyzer, ScreenTool
from jarvis.core.audit import AuditLog
from jarvis.core.config import Settings, get_settings
from jarvis.core.logging import configure_logging
from jarvis.core.safety import SafetyManager
from jarvis.filesystem.agent import FileSystemAgent, FileTool
from jarvis.memory.store import MemoryStore
from jarvis.plugins.loader import PluginLoader
from jarvis.tools.registry import ToolRegistry


@dataclass(slots=True)
class JarvisRuntime:
    settings: Settings
    apps: AppRegistry
    tools: ToolRegistry
    safety: SafetyManager
    audit: AuditLog
    memory: MemoryStore
    planner: IntentPlanner
    executor: AgentExecutor

    def handle_text(self, text: str):
        plan = self.planner.plan(text)
        return plan, self.executor.execute(plan)


def build_runtime() -> JarvisRuntime:
    settings = get_settings()
    configure_logging(settings)
    audit = AuditLog(settings.data_dir / "jarvis.db")
    memory = MemoryStore(settings.data_dir / "jarvis.db")
    safety = SafetyManager(settings)
    apps = AppRegistry()
    tools = ToolRegistry()

    tools.register(AgentTool())
    tools.register(DesktopTool(DesktopController(settings, apps)))
    tools.register(FileTool(FileSystemAgent(settings, safety)))
    tools.register(BrowserTool(BrowserController(settings)))
    tools.register(ClipboardTool(ClipboardManager(settings)))
    tools.register(ScreenTool(ScreenAnalyzer(settings)))

    PluginLoader(settings).load_into(tools)

    planner = IntentPlanner(safety)
    executor = AgentExecutor(settings=settings, tools=tools, safety=safety, audit=audit, memory=memory)
    return JarvisRuntime(settings, apps, tools, safety, audit, memory, planner, executor)
