"""Logging setup for SourceLens AI."""

import logging
import sys

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure root logging once for the application."""

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=False,
    )
