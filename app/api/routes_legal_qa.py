import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.schemas import LegalQARequest
from app.services.legal_qa_service import LegalQAService, get_legal_qa_service

router = APIRouter(tags=["legal-qa"])


@router.post("/legal-qa")
async def legal_qa(
    request: LegalQARequest,
    service: LegalQAService = Depends(get_legal_qa_service),
):
    return await service.answer(request)


@router.post("/legal-qa/stream")
async def legal_qa_stream(
    request: LegalQARequest,
    service: LegalQAService = Depends(get_legal_qa_service),
):
    async def event_stream():
        async for event in service.answer_stream(request):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

