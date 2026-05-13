from app.api.schemas import LegalQARequest


def normalize_request(request: LegalQARequest) -> LegalQARequest:
    request.message = request.message.strip()
    if request.region:
        request.region = request.region.strip()
    return request

