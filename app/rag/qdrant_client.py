from qdrant_client import AsyncQdrantClient

from app.config import get_settings
from app.rag.schemas import SearchQuery, SearchResult


class QdrantSearchClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncQdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key or None,
            timeout=5,
            check_compatibility=False,
        )

    async def search(self, query: SearchQuery, vector: list[float] | None = None) -> list[SearchResult]:
        if not self.settings.rag_index_ready or vector is None:
            return []
        try:
            results = await self.client.search(
                collection_name=self.settings.qdrant_collection,
                query_vector=vector,
                limit=query.top_k,
                with_payload=True,
            )
        except Exception:
            return []
        items: list[SearchResult] = []
        for result in results:
            payload = result.payload or {}
            items.append(SearchResult(relevance_score=float(result.score or 0), **payload))
        return items
