import os

import pytest

from app.rag.qdrant_client import QdrantSearchClient
from app.rag.schemas import SearchQuery


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "true", reason="integration tests are opt-in")
@pytest.mark.asyncio
async def test_qdrant_connection_does_not_raise():
    client = QdrantSearchClient()
    results = await client.search(SearchQuery(query="劳动合同"), vector=[0.0] * 1024)
    assert isinstance(results, list)

