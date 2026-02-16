"""AIDEN Agent Framework - Registry of all available agents."""

from typing import Dict, Type

from app.agents.base.agent import BaseAgent

# Agent registry: maps phase types to agent implementations
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {}


def register_agent(phase_type: str):
    """Decorator to register an agent class for a phase type."""
    def decorator(cls: Type[BaseAgent]):
        AGENT_REGISTRY[phase_type] = cls
        return cls
    return decorator


def get_agent_class(phase_type: str) -> Type[BaseAgent]:
    """Get the agent class registered for a given phase type."""
    if phase_type not in AGENT_REGISTRY:
        raise ValueError(
            f"No agent registered for phase: {phase_type}. "
            f"Available phases: {list(AGENT_REGISTRY.keys())}"
        )
    return AGENT_REGISTRY[phase_type]


# Import agents to trigger registration
from app.agents.ryan.agent import RyanAgent  # noqa: F401, E402
