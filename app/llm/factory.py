from app.config import get_settings
from app.llm.mock import MockLLMClient
from app.llm.openai_compatible import OpenAICompatibleLLMClient


def get_llm_client():
    settings = get_settings()
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMClient(settings)
    return MockLLMClient()

