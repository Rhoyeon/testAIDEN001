"""LLM callback handlers for token tracking and logging."""

from typing import Any, Dict, List
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from app.core.logging import get_logger

logger = get_logger("llm.callbacks")


class TokenTrackingCallback(AsyncCallbackHandler):
    """Tracks token usage across LLM calls."""

    def __init__(self):
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost: float = 0.0
        self.call_count: int = 0

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.call_count += 1
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            self.total_prompt_tokens += usage.get("prompt_tokens", 0)
            self.total_completion_tokens += usage.get("completion_tokens", 0)

    def get_usage_summary(self) -> Dict[str, Any]:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "call_count": self.call_count,
        }

    def reset(self) -> None:
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0


class AgentLLMCallback(AsyncCallbackHandler):
    """Logs LLM calls during agent execution for observability."""

    def __init__(self, agent_name: str, execution_id: str):
        self.agent_name = agent_name
        self.execution_id = execution_id

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        model = serialized.get("kwargs", {}).get("model_name", "unknown")
        logger.info(
            f"[{self.agent_name}:{self.execution_id}] LLM call started | model={model}"
        )

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        usage = {}
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
        logger.info(
            f"[{self.agent_name}:{self.execution_id}] LLM call completed | "
            f"tokens={usage.get('total_tokens', 'N/A')}"
        )

    async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        logger.error(
            f"[{self.agent_name}:{self.execution_id}] LLM call failed | error={error}"
        )
