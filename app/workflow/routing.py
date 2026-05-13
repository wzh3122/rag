from app.workflow.state import LegalQAState


def route_after_facts(state: LegalQAState) -> str:
    status = state.get("status")
    if status in {"out_of_scope", "clarification_needed", "fact_conflict"}:
        return "answer_generation"
    return "legal_retrieval"

