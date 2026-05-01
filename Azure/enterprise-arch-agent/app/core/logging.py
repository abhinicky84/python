from __future__ import annotations

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    get_settings()
    logging.basicConfig(level=logging.CRITICAL, force=True)
    logging.disable(logging.CRITICAL)
