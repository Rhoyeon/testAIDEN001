"""Base agent abstract class - core of the AIDEN agent framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph

from app.config import settings
from app.core.logging import AgentLogger, get_logger
from app.llm.provider import LLMProvider
from app.rag.pipeline import RAGPipeline

logger = get_logger("agents.base")


class BaseAgent(ABC):
    """Abstract base class for all AIDEN agents.

    Each agent implements a LangGraph StateGraph that defines the workflow
    for a specific development phase (analysis, design, development, testing).
    """

    def __init__(
        self,
        agent_name: str,
        llm_provider: LLMProvider,
        rag_pipeline: RAGPipeline,
        event_bus: Any = None,
    ):
        self.agent_name = agent_name
        self.llm_provider = llm_provider
        self.rag_pipeline = rag_pipeline
        self.event_bus = event_bus
        self._compiled_graph = None
        self._logger: AgentLogger | None = None

    def get_logger(self, execution_id: str) -> AgentLogger:
        """Get a logger instance for this agent execution."""
        if self._logger is None or self._logger._context["execution_id"] != execution_id:
            self._logger = AgentLogger(self.agent_name, execution_id)
        return self._logger

    @abstractmethod
    def get_state_class(self) -> Type:
        """Return the TypedDict state class for this agent."""
        ...

    @abstractmethod
    def build_graph(self, builder: StateGraph) -> StateGraph:
        """Define nodes, edges, and conditional routing on the graph builder.

        This method must add all nodes, edges, and conditional edges
        to the builder and return it.
        """
        ...

    def get_interrupt_nodes(self) -> list[str]:
        """Override to specify nodes that should trigger HITL interrupts.

        Nodes listed here will pause execution BEFORE they run,
        allowing human review of the current state.
        """
        return []

    async def compile(self) -> Any:
        """Compile the LangGraph with PostgreSQL checkpointer for durability."""
        builder = StateGraph(self.get_state_class())
        builder = self.build_graph(builder)

        interrupt_nodes = self.get_interrupt_nodes()

        checkpointer = AsyncPostgresSaver.from_conn_string(settings.database_url)
        await checkpointer.setup()

        self._compiled_graph = builder.compile(
            checkpointer=checkpointer,
            interrupt_before=interrupt_nodes if interrupt_nodes else None,
        )

        logger.info(f"Agent '{self.agent_name}' compiled successfully")
        return self._compiled_graph

    async def execute(
        self,
        input_data: dict,
        thread_id: str,
        config_overrides: dict | None = None,
    ) -> dict:
        """Execute the agent graph from the beginning.

        Args:
            input_data: Initial state for the graph
            thread_id: Unique thread ID for checkpointing
            config_overrides: Optional runtime config overrides

        Returns:
            Final state after execution
        """
        if self._compiled_graph is None:
            await self.compile()

        config = {
            "configurable": {
                "thread_id": thread_id,
                **(config_overrides or {}),
            }
        }

        agent_logger = self.get_logger(input_data.get("execution_id", thread_id))
        agent_logger.info("Starting agent execution", thread_id=thread_id)

        result = None
        async for event in self._compiled_graph.astream(
            input_data, config, stream_mode="values"
        ):
            # Emit events for observability
            current_node = event.get("current_node")
            if current_node:
                agent_logger.info(f"Processing node: {current_node}")

            if self.event_bus:
                await self._emit_event("agent.step", {
                    "agent_name": self.agent_name,
                    "thread_id": thread_id,
                    "state": self._sanitize_state(event),
                })

            result = event

        agent_logger.info("Agent execution completed", thread_id=thread_id)
        return result or {}

    async def resume(
        self,
        thread_id: str,
        human_input: Any = None,
    ) -> dict:
        """Resume agent execution after a HITL interrupt.

        Args:
            thread_id: Thread ID of the paused execution
            human_input: Human review decision/feedback to resume with

        Returns:
            Final state after resumed execution
        """
        if self._compiled_graph is None:
            await self.compile()

        from langgraph.types import Command

        config = {"configurable": {"thread_id": thread_id}}

        agent_logger = self.get_logger(thread_id)
        agent_logger.info("Resuming agent execution", human_input=str(human_input)[:100])

        resume_input = Command(resume=human_input) if human_input is not None else None

        result = None
        async for event in self._compiled_graph.astream(
            resume_input, config, stream_mode="values"
        ):
            current_node = event.get("current_node")
            if current_node:
                agent_logger.info(f"Processing node: {current_node}")

            if self.event_bus:
                await self._emit_event("agent.step", {
                    "agent_name": self.agent_name,
                    "thread_id": thread_id,
                    "state": self._sanitize_state(event),
                })

            result = event

        agent_logger.info("Resumed execution completed", thread_id=thread_id)
        return result or {}

    async def get_state(self, thread_id: str) -> dict:
        """Get the current state of a paused agent execution."""
        if self._compiled_graph is None:
            await self.compile()

        config = {"configurable": {"thread_id": thread_id}}
        snapshot = await self._compiled_graph.aget_state(config)
        return snapshot.values if snapshot else {}

    async def _emit_event(self, event_type: str, data: dict) -> None:
        """Emit an event through the event bus if available."""
        if self.event_bus:
            try:
                await self.event_bus.publish(event_type=event_type, data=data)
            except Exception as e:
                logger.warning(f"Failed to emit event: {e}")

    def _sanitize_state(self, state: dict) -> dict:
        """Remove large/sensitive fields from state before emitting."""
        sanitized = {}
        skip_fields = {"messages", "retrieved_context"}
        for key, value in state.items():
            if key in skip_fields:
                sanitized[key] = f"[{len(value)} items]" if isinstance(value, list) else "[redacted]"
            else:
                sanitized[key] = value
        return sanitized
