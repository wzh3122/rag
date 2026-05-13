from typing import Protocol

from app.rag.schemas import SearchQuery, SearchResult


class RagSearchClient(Protocol):
    async def search(self, query: SearchQuery) -> list[SearchResult]:
        ...

