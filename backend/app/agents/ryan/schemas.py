"""Output schemas for Ryan agent structured LLM calls."""

from pydantic import BaseModel, Field


class RequirementOutput(BaseModel):
    """Single requirement extracted by the agent."""
    id: str = Field(description="Unique requirement ID in REQ-XXX format")
    title: str = Field(description="Clear, concise requirement title")
    description: str = Field(description="Detailed requirement description")
    category: str = Field(description="'functional' or 'non_functional'")
    priority: str = Field(description="'high', 'medium', or 'low'")
    source_reference: str = Field(description="Reference to source section in dev request")
    acceptance_criteria: list[str] = Field(description="Testable acceptance criteria")


class RequirementsListOutput(BaseModel):
    """List of requirements extracted from the document."""
    requirements: list[RequirementOutput]


class AmbiguityOutput(BaseModel):
    """Single ambiguity detected in requirements."""
    requirement_id: str = Field(description="ID of the related requirement")
    description: str = Field(description="Description of the ambiguity")
    suggestion: str = Field(description="Suggested clarification")
    severity: str = Field(description="'high', 'medium', or 'low'")


class AmbiguityListOutput(BaseModel):
    """List of ambiguities found in requirements."""
    ambiguities: list[AmbiguityOutput]


class TraceabilityEntryOutput(BaseModel):
    """Single traceability matrix entry."""
    requirement_id: str
    requirement_title: str
    source_section: str
    source_text: str
    verification_method: str


class TraceabilityMatrixOutput(BaseModel):
    """Complete traceability matrix."""
    entries: list[TraceabilityEntryOutput]
