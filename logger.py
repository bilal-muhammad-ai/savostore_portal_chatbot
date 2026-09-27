import logging
from pathlib import Path
from pprint import pformat
from typing import Any

_CONFIGURED = False


def pretty(obj: Any) -> str:
    """Format nested objects for multi-line, human-readable logs."""
    return pformat(obj, indent=2, width=100, sort_dicts=False)


def setup_logging() -> logging.Logger:
    """Configure file + console logging once and return the shared logger."""
    global _CONFIGURED

    logger = logging.getLogger("savostore")
    if _CONFIGURED:
        return logger

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_dir / "savostore.log")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    _CONFIGURED = True
    return logger


logger = setup_logging()
