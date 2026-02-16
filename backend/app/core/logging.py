"""Structured logging configuration for AIDEN platform."""

from __future__ import annotations
import logging
import sys
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = logging.DEBUG if settings.debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(f"aiden.{name}")


class AgentLogger:
    """Specialized logger for agent execution with structured context."""

    def __init__(self, agent_name: str, execution_id: str):
        self._logger = get_logger(f"agent.{agent_name}")
        self._context = {"agent_name": agent_name, "execution_id": execution_id}

    def _format(self, message: str, **kwargs: Any) -> str:
        ctx = {**self._context, **kwargs}
        ctx_str = " | ".join(f"{k}={v}" for k, v in ctx.items() if v is not None)
        return f"{message} | {ctx_str}"

    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(self._format(message, **kwargs))

    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(self._format(message, **kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(self._format(message, **kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(self._format(message, **kwargs))

    def node_enter(self, node_name: str) -> None:
        self.info(f"Entering node: {node_name}", node=node_name)

    def node_exit(self, node_name: str, duration_ms: int | None = None) -> None:
        self.info(f"Exiting node: {node_name}", node=node_name, duration_ms=duration_ms)

    def hitl_interrupt(self, reason: str) -> None:
        self.info(f"HITL interrupt: {reason}", event="hitl_interrupt")
