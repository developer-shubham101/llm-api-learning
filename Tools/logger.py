import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR   = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE  = os.path.join(LOG_DIR, "tools.log")
FLOW_FILE = os.path.join(LOG_DIR, "flow.log")

os.makedirs(LOG_DIR, exist_ok=True)

_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)-8s] %(name)s :: %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

def _make_file_handler(path: str, level: int) -> RotatingFileHandler:
    h = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    h.setLevel(level)
    h.setFormatter(_fmt)
    return h

def _make_console_handler() -> logging.StreamHandler:
    h = logging.StreamHandler()
    h.setLevel(logging.WARNING)   # keep console clean — only warnings/errors
    h.setFormatter(_fmt)
    return h

# Shared flow logger — every module writes here for full trace
_flow_logger = logging.getLogger("flow")
if not _flow_logger.handlers:
    _flow_logger.setLevel(logging.DEBUG)
    _flow_logger.addHandler(_make_file_handler(FLOW_FILE, logging.DEBUG))
    _flow_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.addHandler(_make_console_handler())
    logger.addHandler(_make_file_handler(LOG_FILE, logging.DEBUG))
    return logger


def log_section(title: str):
    """Write a visual section separator to the flow log."""
    bar = "=" * 60
    _flow_logger.debug("\n%s\n  %s\n%s", bar, title.upper(), bar)


def flow(msg: str, *args):
    """Log a flow step — always goes to flow.log at DEBUG level."""
    _flow_logger.debug(msg, *args)
