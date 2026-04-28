from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler

from jarvis.core.config import Settings


def configure_logging(settings: Settings) -> None:
    log_path = settings.data_dir / "logs" / "jarvis.log"
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(settings.log_level.upper())

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console_handler = RichHandler(rich_tracebacks=True, show_time=False)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(console_handler)
