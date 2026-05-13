from app.config import get_settings
from app.rag.reranker.mock import MockRerankerProvider
from app.rag.reranker.openai_compatible import OpenAICompatibleRerankerProvider


def get_reranker_provider():
    settings = get_settings()
    if settings.reranker_provider == "openai_compatible":
        return OpenAICompatibleRerankerProvider(settings)
    return MockRerankerProvider()

