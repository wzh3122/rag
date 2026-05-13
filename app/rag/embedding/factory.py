from app.config import get_settings
from app.rag.embedding.mock import MockEmbeddingProvider
from app.rag.embedding.openai_compatible import OpenAICompatibleEmbeddingProvider


def get_embedding_provider():
    settings = get_settings()
    if settings.embedding_provider == "openai_compatible":
        return OpenAICompatibleEmbeddingProvider(settings)
    return MockEmbeddingProvider()

