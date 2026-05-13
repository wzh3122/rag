from typing import Any, TypedDict

from app.api.schemas import LegalSource, ReviewResult


class LegalQAState(TypedDict, total=False):
    session_id: str
    message: str
    legal_domain: str
    region: str | None
    previous_facts: dict[str, Any]
    facts: dict[str, Any]
    status: str
    questions: list[str]
    missing_info: list[str]
    conflicts: list[dict[str, str]]
    sources: list[LegalSource]
    final_answer: str
    review: ReviewResult
    retry_count: int
    trace_summary: list[dict[str, Any]]

