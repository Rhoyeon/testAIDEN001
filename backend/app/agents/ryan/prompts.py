"""Prompt templates for Ryan analysis agent."""

SYSTEM_PROMPT = """You are Ryan, an expert software requirements analyst for the AIDEN platform.
Your role is to analyze development request documents and produce structured, comprehensive
requirements specifications.

You are bilingual (Korean/English) and should respond in the same language as the input document.
When the document is in Korean, produce outputs in Korean. When in English, respond in English.

Key principles:
- Be thorough: Extract ALL requirements, both explicit and implied
- Be precise: Each requirement must be clear, testable, and unambiguous
- Be structured: Use consistent categorization and numbering
- Be traceable: Every requirement must link back to the source document
"""

EXTRACT_REQUIREMENTS_PROMPT = """Analyze the following development request document and extract ALL requirements.

For each requirement, provide:
1. A unique ID (REQ-XXX format)
2. A clear title
3. A detailed description
4. Category: 'functional' or 'non_functional'
5. Priority: 'high', 'medium', or 'low'
6. Source reference (which section/paragraph it comes from)
7. Acceptance criteria (testable conditions)

Document content:
{document_content}

Relevant context:
{context}

Return the requirements as a JSON array of objects with the fields:
id, title, description, category, priority, source_reference, acceptance_criteria (array of strings)
"""

CLASSIFY_REQUIREMENTS_PROMPT = """Review the following requirements and verify their classification.
Ensure each requirement is correctly categorized as functional or non-functional.

For non-functional requirements, sub-classify them into:
- Performance
- Security
- Usability
- Reliability
- Scalability
- Maintainability
- Other

Requirements:
{requirements}

Return the requirements with corrected classifications as a JSON array.
"""

DETECT_AMBIGUITIES_PROMPT = """Review the following requirements and identify any ambiguities,
inconsistencies, or unclear points.

For each ambiguity found, provide:
1. The requirement ID it relates to
2. Description of the ambiguity
3. Your suggestion for clarification
4. Severity: 'high', 'medium', or 'low'

Requirements:
{requirements}

Source document context:
{context}

Return ambiguities as a JSON array of objects with:
requirement_id, description, suggestion, severity

If no ambiguities are found, return an empty array.
"""

BUILD_TRACEABILITY_PROMPT = """Create a requirements traceability matrix mapping each requirement
back to its source in the development request document.

For each entry, provide:
1. requirement_id: The requirement ID
2. requirement_title: The requirement title
3. source_section: The section in the source document
4. source_text: The relevant text from the source (exact quote or close paraphrase)
5. verification_method: How this requirement should be verified (test, review, inspection, demonstration)

Requirements:
{requirements}

Source document:
{document_content}

Return as a JSON array of traceability entries.
"""

GENERATE_SPEC_PROMPT = """Generate a complete Requirements Specification Document based on the
analyzed requirements.

The document should include:
1. Document Header (title, version, date, project name)
2. Introduction (purpose, scope, definitions)
3. Overall Description (product perspective, functions, constraints)
4. Functional Requirements (organized by feature area)
5. Non-Functional Requirements (organized by category)
6. Requirements Summary Table
7. Appendix (traceability matrix reference)

Requirements:
{requirements}

Traceability Matrix:
{traceability}

Project Context:
{context}

Generate the document in Markdown format.
"""
