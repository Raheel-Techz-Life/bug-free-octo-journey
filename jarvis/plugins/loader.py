from __future__ import annotations

import importlib
import logging
import sys

from jarvis.core.config import Settings
from jarvis.plugins.builtin.vscode import VSCodePlugin
from jarvis.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def load_into(self, registry: ToolRegistry) -> None:
        VSCodePlugin().register(registry)
        plugin_dir = self.settings.plugins_dir or (self.settings.data_dir / "plugins")
        if not plugin_dir.exists():
            return
        sys.path.insert(0, str(plugin_dir))
        for manifest in plugin_dir.glob("*/plugin.py"):
            module_name = f"{manifest.parent.name}.plugin"
            try:
                module = importlib.import_module(module_name)
                plugin = module.create_plugin()
                plugin.register(registry)
                logger.info("Loaded plugin %s", getattr(plugin, "name", module_name))
            except Exception:
                logger.exception("Failed to load plugin from %s", manifest)
