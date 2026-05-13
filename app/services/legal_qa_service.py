from collections.abc import AsyncIterator
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.schemas import FactConflictItem, LegalQARequest, LegalQAResponse, ReviewResult
from app.db.database import get_db
from app.db.repositories import SessionRepository
from app.workflow.graph import build_legal_qa_graph
from app.workflow.state import LegalQAState


class LegalQAService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SessionRepository(db)
        self.graph = build_legal_qa_graph()

    async def answer(self, request: LegalQARequest) -> LegalQAResponse:
        session = self.repository.get_or_create(request.session_id)
        previous_facts = self.repository.get_facts(session)
        self.repository.add_message(session.id, "user", request.message)

        state: LegalQAState = {
            "session_id": session.id,
            "message": request.message.strip(),
            "legal_domain": request.legal_domain or previous_facts.get("legal_domain", "unknown"),
            "region": request.region or previous_facts.get("region"),
            "previous_facts": previous_facts,
            "retry_count": 0,
            "trace_summary": [],
        }
        final_state = await self.graph.ainvoke(state)
        response = self._to_response(session.id, request, final_state)

        self.repository.update_session(
            session,
            status=response.status,
            legal_domain=response.legal_domain,
            region=response.region,
            facts=response.extracted_facts,
            final_answer=response.final_answer,
            retry_count=response.review.retry_count,
        )
        if response.sources:
            self.repository.replace_sources(session.id, response.sources)
        if response.final_answer:
            self.repository.add_message(session.id, "assistant", response.final_answer)
        self.repository.add_trace(
            session.id,
            "workflow",
            response.status,
            {"message": request.message, "legal_domain": request.legal_domain, "region": request.region},
            {"status": response.status, "source_count": len(response.sources)},
        )
        return response

    async def answer_stream(self, request: LegalQARequest) -> AsyncIterator[dict[str, Any]]:
        session = self.repository.get_or_create(request.session_id)
        yield {"type": "session", "session_id": session.id}
        stages = [
            ("controller", "正在创建或读取会话"),
            ("fact_extractor", "正在提取关键事实"),
            ("legal_retriever", "正在检索法规依据"),
            ("answer_generator", "正在生成回答"),
            ("reviewer", "正在检查回答可靠性"),
        ]
        for agent, message in stages:
            yield {"type": "stage", "agent": agent, "message": message}
        response = await self.answer(LegalQARequest(**request.model_dump(exclude={"session_id"}), session_id=session.id))
        if response.sources:
            yield {"type": "sources", "data": [source.model_dump() for source in response.sources]}
        if response.status in {"clarification_needed", "fact_conflict", "general_reference", "insufficient_basis"}:
            yield {"type": response.status, "data": response.model_dump()}
        yield {"type": "final", "data": response.model_dump()}

    def _to_response(self, session_id: str, request: LegalQARequest, state: LegalQAState) -> LegalQAResponse:
        status = state.get("status", "error")
        facts = state.get("facts", {})
        if status == "out_of_scope":
            return LegalQAResponse(
                session_id=session_id,
                status="out_of_scope",
                question=request.message,
                legal_domain=facts.get("legal_domain", state.get("legal_domain", "unknown")),
                region=state.get("region"),
                extracted_facts=facts,
                sources=[],
                final_answer=state.get("final_answer", ""),
                review=ReviewResult(passed=True),
                message="当前版本仅支持中国大陆法律的一般信息参考, 不支持该法域问题。",
            )
        if status == "clarification_needed":
            return LegalQAResponse(
                session_id=session_id,
                status=status,
                question=request.message,
                legal_domain=facts.get("legal_domain", "unknown"),
                region=state.get("region"),
                extracted_facts=facts,
                sources=[],
                final_answer="",
                review=ReviewResult(passed=True),
                questions=state.get("questions", []),
                known_facts=facts,
                missing_info=state.get("missing_info", []),
            )
        if status == "fact_conflict":
            return LegalQAResponse(
                session_id=session_id,
                status=status,
                question=request.message,
                legal_domain=facts.get("legal_domain", "unknown"),
                region=state.get("region"),
                extracted_facts=facts,
                sources=[],
                final_answer="",
                review=ReviewResult(passed=True),
                conflicts=[FactConflictItem(**item) for item in state.get("conflicts", [])],
            )
        return LegalQAResponse(
            session_id=session_id,
            status=status,
            question=request.message,
            legal_domain=facts.get("legal_domain", state.get("legal_domain", "unknown")),
            region=state.get("region"),
            extracted_facts=facts,
            sources=state.get("sources", []),
            final_answer=state.get("final_answer", ""),
            review=state.get("review", ReviewResult(passed=False, issues=["workflow did not run reviewer"])),
            trace_summary=state.get("trace_summary", []),
            message="当前法规库尚未检索到可支撑具体法律结论的依据, 以下仅为一般处理思路。"
            if status == "general_reference"
            else None,
        )


def get_legal_qa_service(db: Session = Depends(get_db)) -> LegalQAService:
    return LegalQAService(db)

