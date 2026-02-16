"""Phase transition controller - manages the flow between development phases."""

from typing import List

from app.core.logging import get_logger

logger = get_logger("orchestration.phase_controller")

# Ordered list of development phases
PHASE_ORDER: List[str] = ["analysis", "design", "development", "testing"]

# Agent assignments per phase
PHASE_AGENTS = {
    "analysis": "ryan",
    "design": None,      # TBD
    "development": None,  # TBD
    "testing": None,      # TBD
}


class PhaseController:
    """Controls phase transitions in a project workflow."""

    @staticmethod
    def get_next_phase(current_phase: str) -> str | None:
        """Get the next phase after the current one."""
        try:
            idx = PHASE_ORDER.index(current_phase)
            if idx + 1 < len(PHASE_ORDER):
                return PHASE_ORDER[idx + 1]
            return None
        except ValueError:
            logger.error(f"Unknown phase: {current_phase}")
            return None

    @staticmethod
    def get_agent_for_phase(phase_type: str) -> str | None:
        """Get the agent name assigned to a phase."""
        return PHASE_AGENTS.get(phase_type)

    @staticmethod
    def is_phase_ready(phase_type: str) -> bool:
        """Check if a phase has an agent assigned and is ready to execute."""
        agent = PHASE_AGENTS.get(phase_type)
        return agent is not None

    @staticmethod
    def get_all_phases() -> List[dict]:
        """Get all phases with their order and agent assignments."""
        return [
            {
                "phase_type": phase,
                "phase_order": i + 1,
                "agent_name": PHASE_AGENTS.get(phase),
                "is_ready": PHASE_AGENTS.get(phase) is not None,
            }
            for i, phase in enumerate(PHASE_ORDER)
        ]

    @staticmethod
    def is_final_phase(phase_type: str) -> bool:
        """Check if this is the last phase."""
        return phase_type == PHASE_ORDER[-1]
