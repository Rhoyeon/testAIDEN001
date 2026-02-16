"""LLM model registry and configuration."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    provider: str
    model_name: str
    max_tokens: int = 4096
    temperature: float = 0.1
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


# Model registry with known models and their configurations
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    # OpenAI
    "gpt-4.1": ModelConfig(
        provider="openai", model_name="gpt-4.1",
        max_tokens=32768, cost_per_1k_input=0.002, cost_per_1k_output=0.008,
    ),
    "gpt-4.1-mini": ModelConfig(
        provider="openai", model_name="gpt-4.1-mini",
        max_tokens=16384, cost_per_1k_input=0.0004, cost_per_1k_output=0.0016,
    ),
    "gpt-4o": ModelConfig(
        provider="openai", model_name="gpt-4o",
        max_tokens=16384, cost_per_1k_input=0.0025, cost_per_1k_output=0.01,
    ),
    # Anthropic
    "claude-sonnet-4": ModelConfig(
        provider="anthropic", model_name="claude-sonnet-4-20250514",
        max_tokens=8192, cost_per_1k_input=0.003, cost_per_1k_output=0.015,
    ),
    "claude-haiku-3.5": ModelConfig(
        provider="anthropic", model_name="claude-3-5-haiku-20241022",
        max_tokens=8192, cost_per_1k_input=0.0008, cost_per_1k_output=0.004,
    ),
}

# Task-to-model mapping: which model to use for each task type
DEFAULT_TASK_MODEL_MAP: Dict[str, str] = {
    "requirement_extraction": "gpt-4.1",
    "requirement_classification": "gpt-4.1-mini",
    "ambiguity_detection": "gpt-4.1",
    "document_generation": "gpt-4.1",
    "traceability_mapping": "gpt-4.1-mini",
    "code_generation": "claude-sonnet-4",
    "code_review": "claude-sonnet-4",
    "test_generation": "gpt-4.1",
    "summarization": "gpt-4.1-mini",
}


def get_model_config(model_key: str) -> ModelConfig:
    """Get model configuration by key."""
    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_key}. Available: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[model_key]


def get_model_for_task(task_type: str, task_model_map: Dict[str, str] | None = None) -> ModelConfig:
    """Get the recommended model for a task type."""
    mapping = task_model_map or DEFAULT_TASK_MODEL_MAP
    model_key = mapping.get(task_type)
    if not model_key:
        model_key = "gpt-4.1"  # fallback
    return get_model_config(model_key)
