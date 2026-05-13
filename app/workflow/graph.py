from langgraph.graph import END, StateGraph

from app.agents.answer_generator import generate_completed_answer, generate_general_reference_answer
from app.agents.fact_extractor import (
    detect_conflicts,
    detect_out_of_scope,
    extract_facts,
    needs_clarification,
)
from app.agents.legal_retriever import retrieve_sources
from app.agents.reviewer import review_answer
from app.workflow.routing import route_after_facts
from app.workflow.state import LegalQAState


async def fact_extraction_node(state: LegalQAState) -> LegalQAState:
    message = state["message"]
    if detect_out_of_scope(message):
        state["status"] = "out_of_scope"
        state["facts"] = dict(state.get("previous_facts", {}))
        return state

    facts = extract_facts(
        message,
        state.get("legal_domain"),
        state.get("region"),
        state.get("previous_facts", {}),
    )
    state["facts"] = facts
    state["legal_domain"] = facts.get("legal_domain", "unknown")
    need_more, questions, missing = needs_clarification(message, state["legal_domain"])
    conflicts = detect_conflicts(state.get("previous_facts", {}), facts)
    if conflicts:
        state["status"] = "fact_conflict"
        state["conflicts"] = conflicts
    elif need_more:
        state["status"] = "clarification_needed"
        state["questions"] = questions
        state["missing_info"] = missing
    else:
        state["status"] = "retrieval_ready"
        state["missing_info"] = missing
    return state


async def legal_retrieval_node(state: LegalQAState) -> LegalQAState:
    state["sources"] = await retrieve_sources(
        state["message"],
        state.get("legal_domain", "unknown"),
        state.get("region"),
    )
    return state


async def answer_generation_node(state: LegalQAState) -> LegalQAState:
    status = state.get("status")
    if status == "out_of_scope":
        state["final_answer"] = "当前版本仅支持中国大陆法律的一般信息参考, 不支持该法域问题。"
        return state
    if status in {"clarification_needed", "fact_conflict"}:
        state["final_answer"] = ""
        return state

    sources = state.get("sources", [])
    if sources:
        state["status"] = "completed"
        state["final_answer"] = generate_completed_answer(
            state["message"],
            state.get("facts", {}),
            sources,
            state.get("region"),
        )
    else:
        state["status"] = "general_reference"
        state["final_answer"] = generate_general_reference_answer(
            state["message"],
            state.get("facts", {}),
            state.get("region"),
        )
    return state


async def reviewer_node(state: LegalQAState) -> LegalQAState:
    if state.get("status") in {"completed", "general_reference"}:
        state["review"] = review_answer(
            state["status"],
            state.get("final_answer", ""),
            state.get("sources", []),
            state.get("retry_count", 0),
        )
    return state


def build_legal_qa_graph():
    graph = StateGraph(LegalQAState)
    graph.add_node("fact_extraction", fact_extraction_node)
    graph.add_node("legal_retrieval", legal_retrieval_node)
    graph.add_node("answer_generation", answer_generation_node)
    graph.add_node("reviewer", reviewer_node)
    graph.set_entry_point("fact_extraction")
    graph.add_conditional_edges(
        "fact_extraction",
        route_after_facts,
        {
            "legal_retrieval": "legal_retrieval",
            "answer_generation": "answer_generation",
        },
    )
    graph.add_edge("legal_retrieval", "answer_generation")
    graph.add_edge("answer_generation", "reviewer")
    graph.add_edge("reviewer", END)
    return graph.compile()

