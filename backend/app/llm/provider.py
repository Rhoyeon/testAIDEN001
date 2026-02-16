"""Multi-LLM provider factory with unified interface."""

from typing import Any, Dict

from langchain_core.language_models import BaseChatModel

from app.config import settings
from app.core.logging import get_logger
from app.llm.callbacks import AgentLLMCallback, TokenTrackingCallback
from app.llm.models import DEFAULT_TASK_MODEL_MAP, MODEL_REGISTRY, ModelConfig

logger = get_logger("llm.provider")


class LLMProvider:
    """Factory for creating and caching LLM instances with unified interface."""

    def __init__(self, task_model_map: Dict[str, str] | None = None):
        self._model_cache: Dict[str, BaseChatModel] = {}
        self._task_model_map = task_model_map or DEFAULT_TASK_MODEL_MAP

    def get_model(
        self,
        model_key: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        streaming: bool = True,
        callbacks: list | None = None,
    ) -> BaseChatModel:
        """Get or create a cached LLM instance."""
        model_key = model_key or settings.default_llm_model
        model_config = MODEL_REGISTRY.get(model_key)
        if not model_config:
            raise ValueError(f"Unknown model key: {model_key}")

        temp = temperature if temperature is not None else settings.default_llm_temperature
        tokens = max_tokens or model_config.max_tokens

        cache_key = f"{model_key}:{temp}:{tokens}:{streaming}"
        if cache_key not in self._model_cache:
            self._model_cache[cache_key] = self._create_model(
                model_config, temp, tokens, streaming, callbacks
            )

        return self._model_cache[cache_key]

    def get_model_for_task(
        self,
        task_type: str,
        temperature: float | None = None,
        callbacks: list | None = None,
    ) -> BaseChatModel:
        """Get the recommended model for a specific task type."""
        model_key = self._task_model_map.get(task_type, settings.default_llm_model)
        return self.get_model(model_key=model_key, temperature=temperature, callbacks=callbacks)

    def _create_model(
        self,
        config: ModelConfig,
        temperature: float,
        max_tokens: int,
        streaming: bool,
        callbacks: list | None = None,
    ) -> BaseChatModel:
        """Create a new LLM instance based on provider."""
        logger.info(f"Creating LLM instance: {config.provider}/{config.model_name}")

        if config.provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                api_key=settings.openai_api_key,
                callbacks=callbacks,
            )
        elif config.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                api_key=settings.anthropic_api_key,
                callbacks=callbacks,
            )
        elif config.provider == "azure_openai":
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(
                model=config.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
                callbacks=callbacks,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._model_cache.clear()
