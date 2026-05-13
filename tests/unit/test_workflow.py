import pytest

from app.api.schemas import LegalQARequest
from app.db.database import SessionLocal, init_db
from app.services.legal_qa_service import LegalQAService


@pytest.mark.asyncio
async def test_legal_qa_returns_general_reference_when_rag_empty():
    init_db()
    db = SessionLocal()
    try:
        service = LegalQAService(db)
        response = await service.answer(
            LegalQARequest(message="公司拖欠工资三个月, 我可以离职并要求补偿吗?", legal_domain="labor", region="广东")
        )
        assert response.status == "general_reference"
        assert response.sources == []
        assert "免责声明" in response.final_answer
    finally:
        db.close()


@pytest.mark.asyncio
async def test_clarification_needed_for_generic_question():
    init_db()
    db = SessionLocal()
    try:
        service = LegalQAService(db)
        response = await service.answer(LegalQARequest(message="怎么办"))
        assert response.status == "clarification_needed"
        assert response.questions
    finally:
        db.close()


@pytest.mark.asyncio
async def test_fact_conflict_for_session_facts():
    init_db()
    db = SessionLocal()
    try:
        service = LegalQAService(db)
        first = await service.answer(LegalQARequest(message="公司拖欠工资三个月, 我还在职", legal_domain="labor"))
        second = await service.answer(
            LegalQARequest(session_id=first.session_id, message="工资已经发了, 只是加班费没发", legal_domain="labor")
        )
        assert second.status == "fact_conflict"
        assert second.conflicts
    finally:
        db.close()

