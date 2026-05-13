from opensearchpy import AsyncOpenSearch

from app.config import get_settings
from app.rag.schemas import SearchQuery, SearchResult


class OpenSearchSearchClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenSearch(
            hosts=[self.settings.opensearch_url],
            http_auth=(self.settings.opensearch_username, self.settings.opensearch_password),
            use_ssl=self.settings.opensearch_url.startswith("https"),
            verify_certs=False,
            timeout=5,
        )

    async def search(self, query: SearchQuery) -> list[SearchResult]:
        if not self.settings.rag_index_ready:
            return []
        body = {
            "size": query.top_k,
            "query": {
                "multi_match": {
                    "query": query.query,
                    "fields": ["title^3", "text", "article_no^2"],
                }
            },
        }
        try:
            response = await self.client.search(index=self.settings.opensearch_index, body=body)
        except Exception:
            return []
        hits = response.get("hits", {}).get("hits", [])
        return [SearchResult(relevance_score=float(hit.get("_score") or 0), **hit.get("_source", {})) for hit in hits]

