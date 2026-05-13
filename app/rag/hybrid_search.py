from app.api.schemas import LegalSource
from app.rag.embedding.factory import get_embedding_provider
from app.rag.opensearch_client import OpenSearchSearchClient
from app.rag.qdrant_client import QdrantSearchClient
from app.rag.reranker.factory import get_reranker_provider
from app.rag.schemas import SearchQuery, SearchResult


class HybridLegalSearchClient:
    def __init__(self):
        self.embedding = get_embedding_provider()
        self.reranker = get_reranker_provider()
        self.qdrant = QdrantSearchClient()
        self.opensearch = OpenSearchSearchClient()

    async def search(self, query: SearchQuery) -> list[LegalSource]:
        vector: list[float] | None = None
        try:
            vector = (await self.embedding.embed_texts([query.query]))[0]
        except Exception:
            vector = None

        vector_results = await self.qdrant.search(query, vector)
        keyword_results = await self.opensearch.search(query)
        merged = self._merge(vector_results + keyword_results)
        if not merged:
            return []

        reranked_docs = await self.reranker.rerank(
            query.query,
            [item.model_dump() for item in merged],
            top_k=query.top_k,
        )
        return [LegalSource(**doc) for doc in reranked_docs]

    def _merge(self, results: list[SearchResult]) -> list[SearchResult]:
        seen: set[str] = set()
        merged: list[SearchResult] = []
        for item in sorted(results, key=lambda result: result.relevance_score, reverse=True):
            key = f"{item.title}:{item.url}:{item.quote_text}"
            if key in seen:
                continue
            seen.add(key)
            if item.authority_level == "D" or item.effective_status == "obsolete":
                continue
            merged.append(item)
        return merged

