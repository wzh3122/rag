import os

import pytest

from app.rag.opensearch_client import OpenSearchSearchClient
from app.rag.schemas import SearchQuery


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "true", reason="integration tests are opt-in")
@pytest.mark.asyncio
async def test_opensearch_connection_does_not_raise():
    client = OpenSearchSearchClient()
    results = await client.search(SearchQuery(query="劳动合同"))
    assert isinstance(results, list)

