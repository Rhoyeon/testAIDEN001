"""Custom exception hierarchy for AIDEN platform."""

from typing import Any


class AIDENException(Exception):
    """Base exception for all AIDEN errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class NotFoundError(AIDENException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class ValidationError(AIDENException):
    """Input validation failed."""

    def __init__(self, message: str, details: Any = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class AgentExecutionError(AIDENException):
    """Agent execution failed."""

    def __init__(self, agent_name: str, message: str, details: Any = None):
        super().__init__(
            message=f"Agent '{agent_name}' failed: {message}",
            code="AGENT_EXECUTION_FAILED",
            details={"agent_name": agent_name, **(details or {})},
        )


class HITLTimeoutError(AIDENException):
    """HITL review timed out."""

    def __init__(self, review_id: str):
        super().__init__(
            message=f"HITL review timed out: {review_id}",
            code="HITL_TIMEOUT",
            details={"review_id": review_id},
        )


class LLMProviderError(AIDENException):
    """LLM provider call failed."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"LLM provider '{provider}' error: {message}",
            code="LLM_PROVIDER_ERROR",
            details={"provider": provider},
        )


class RAGPipelineError(AIDENException):
    """RAG pipeline processing failed."""

    def __init__(self, stage: str, message: str):
        super().__init__(
            message=f"RAG pipeline error at '{stage}': {message}",
            code="RAG_PIPELINE_ERROR",
            details={"stage": stage},
        )


class DocumentProcessingError(AIDENException):
    """Document loading or processing failed."""

    def __init__(self, document_id: str, message: str):
        super().__init__(
            message=f"Document processing failed for '{document_id}': {message}",
            code="DOCUMENT_PROCESSING_ERROR",
            details={"document_id": document_id},
        )
