from typing import Any, Literal

from pydantic import BaseModel, Field


LegalDomain = Literal[
    "labor",
    "contract",
    "marriage_family",
    "tort",
    "private_lending",
    "housing_lease",
    "consumer_rights",
    "unknown",
]


class LegalQARequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)
    legal_domain: LegalDomain | None = None
    region: str | None = None


class LegalSource(BaseModel):
    title: str
    url: str | None = None
    source: str | None = None
    snippet: str | None = None
    quote_text: str | None = None
    authority_level: str = "unknown"
    effective_status: str = "unknown"
    basis_type: str = "unknown"
    relevance_score: float = 0.0
    used_for: str | None = None


class ReviewResult(BaseModel):
    passed: bool = True
    issues: list[str] = Field(default_factory=list)
    retry_count: int = 0


class ClarificationResponse(BaseModel):
    session_id: str
    status: Literal["clarification_needed"]
    questions: list[str]
    known_facts: dict[str, Any] = Field(default_factory=dict)
    missing_info: list[str] = Field(default_factory=list)


class FactConflictItem(BaseModel):
    field: str
    previous_fact: str
    new_fact: str
    question: str


class LegalQAResponse(BaseModel):
    session_id: str
    status: str
    question: str
    legal_domain: LegalDomain = "unknown"
    region: str | None = None
    extracted_facts: dict[str, Any] = Field(default_factory=dict)
    sources: list[LegalSource] = Field(default_factory=list)
    final_answer: str = ""
    review: ReviewResult = Field(default_factory=ReviewResult)
    trace_summary: list[dict[str, Any]] = Field(default_factory=list)
    message: str | None = None
    questions: list[str] | None = None
    known_facts: dict[str, Any] | None = None
    missing_info: list[str] | None = None
    conflicts: list[FactConflictItem] | None = None

