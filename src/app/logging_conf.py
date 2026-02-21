"""
Structured logging configuration.
"""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with structured format."""
    logging.basicConfig(
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=getattr(logging, level.upper(), logging.INFO),
    )
